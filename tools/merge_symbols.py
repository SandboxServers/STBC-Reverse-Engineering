"""Blend the address-anchored symbol export (this repo) with the semantic
ABI export vendored under tools/abi_export/.

Location layer  : tools/function_names_export.txt   (address -> name)
Meaning layer   : tools/abi_export/stbc_symbols.csv  (c_symbol -> owning_class,
                  stbc_methods.csv, stbc_classes.csv, stbc_constants.csv)

The meaning layer originates in the open_stbc repo (built by
tools/probes/build_ghidra_export.py from the q13 console-probe dumps) and is
vendored here so this repo has no cross-repo dependency.  To refresh it, either
re-copy the four CSVs into tools/abi_export/, or point ABI_EXPORT at the
upstream ghidra_export directory for a one-off run.

Output (tools/merged/):
    stbc_merged_symbols.csv   one row per address, enriched with ABI semantics
    stbc_constants.csv        pass-through of the valued-constant dictionary
    stbc_merge_report.txt     match/residual accounting

Run with any Python 3 (stdlib only), e.g. the open_stbc venv:
    /c/projects/open_stbc/.venv/Scripts/python.exe tools/merge_symbols.py
"""
import csv
import os
import pathlib

# --------------------------------------------------------------------------- #
# Paths.  ABI_EXPORT can be overridden via env to point at a fresh upstream
# ghidra_export dir; by default we read the vendored copy under tools/abi_export.
REPO = pathlib.Path(__file__).resolve().parent.parent
OURS = REPO / "tools" / "function_names_export.txt"
GE = pathlib.Path(
    os.environ.get("ABI_EXPORT", str(REPO / "tools" / "abi_export"))
)
OUT = REPO / "tools" / "merged"
OUT.mkdir(exist_ok=True)

# SWIG module-level helpers that SWIG auto-generates per class.  These are named
# <Class>_<helper> and are NOT enumerated as instance methods in the ABI export.
# The owning class is USUALLY in stbc_classes.csv (then we get ancestors too), but
# some helper-only classes were never dumped by the q13 probe -- we still resolve
# the shape and just leave ancestors blank.
SWIG_HELPERS = {
    "Create", "CreateW", "CreateNull", "Cast",
    "GetObject", "GetObjectByID", "GetNumClassObjects", "GetObjectBySetName",
}


def load_ours():
    """[(address, raw_name)] from the address-anchored export."""
    rows = []
    with OURS.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            addr, _, name = line.partition(",")
            rows.append((addr.strip(), name.strip()))
    return rows


def load_symbols():
    """c_symbol -> {owning_class, method, binding_kind, n_python_aliases}."""
    by_symbol = {}
    with (GE / "stbc_symbols.csv").open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            by_symbol[r["c_symbol"]] = r
    return by_symbol


def load_methods():
    """Two indexes over stbc_methods.csv:
    - by c_symbol            (owning-class-form wrapper names)
    - by python_class_method (python-class-form wrapper names)
    """
    by_symbol = {}
    by_pyclass = {}
    with (GE / "stbc_methods.csv").open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            by_symbol.setdefault(r["c_symbol"], r)
            by_pyclass.setdefault(f'{r["python_class"]}_{r["method"]}', r)
    return by_symbol, by_pyclass


def load_classes():
    """class -> {is_ptr, direct_bases, ancestors} from stbc_classes.csv."""
    classes = {}
    with (GE / "stbc_classes.csv").open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            classes[r["class"]] = r
    return classes


# --------------------------------------------------------------------------- #
def classify(name):
    """Bucket a raw name from the location layer for the `category` column."""
    if name.startswith("swig_"):
        return "swig"
    if name.startswith(("NiRegister_", "NiFactory_")):
        return "nirtti_factory"
    if name.startswith("Handler_"):
        return "re_dispatcher_handler"
    if name.startswith(("py", "PyObject", "PyDict")):
        return "python_capi"
    if name.endswith("_ctor"):
        return "ctor"
    if "dtor" in name:
        return "dtor"
    if "_vfn" in name:
        return "vtable_fn"
    if "EventHandler" in name or name.endswith("Handler"):
        return "event_handler"
    return "engine_internal"


def longest_class_prefix(key, classes):
    """For `Class_field...`, return the longest known-class prefix, or ''.
    Handles field names that themselves contain underscores (m_fLeft)."""
    parts = key.split("_")
    for i in range(len(parts) - 1, 0, -1):
        cand = "_".join(parts[:i])
        if cand in classes:
            return cand
    return ""


def enrich_swig(name, sym_idx, meth_by_sym, meth_by_pyclass, classes):
    """Return (owning_class, python_class, method, binding_kind, join_key)."""
    key = name[len("swig_"):]  # strip prefix

    # 1) exact owning-class-form match (the 'direct' bulk)
    if key in sym_idx:
        s = sym_idx[key]
        return s["owning_class"], "", s["method"], s["binding_kind"], "c_symbol"
    if key in meth_by_sym:
        m = meth_by_sym[key]
        return (m["owning_class"], m["python_class"], m["method"],
                m["binding_kind"], "c_symbol")

    # 2) python-class-form match (Class_Method where Class is the python class)
    if key in meth_by_pyclass:
        m = meth_by_pyclass[key]
        return (m["owning_class"], m["python_class"], m["method"],
                m["binding_kind"], "python_class_method")

    # 3) SWIG object ctor/dtor: new_<Class> / delete_<Class>
    for pfx, kind in (("new_", "swig_ctor"), ("delete_", "swig_dtor")):
        if key.startswith(pfx):
            cls = key[len(pfx):]
            return cls, cls, pfx.rstrip("_"), kind, "swig_ctor_dtor"

    # 4) SWIG struct field accessor: <Class>_<field>_set / _get
    if key.endswith("_set") or key.endswith("_get"):
        cls = longest_class_prefix(key[:-4], classes)
        field = key[:-4]
        if cls:
            field = key[len(cls) + 1:-4]
        return cls, cls, field, "swig_field_accessor", "swig_accessor"

    # 5) SWIG auto-helper: <Class>_<helper>.  Class need NOT be in the ABI dump;
    #    ancestors are only filled in later if the class is known.
    cls, _, helper = key.rpartition("_")
    if helper in SWIG_HELPERS and cls:
        return cls, cls, helper, "swig_helper", "swig_helper_synth"

    # 6) Last resort: leading token is a known class but ge's method dump lacks
    #    this method (static/module-level methods the q13 probe didn't enumerate).
    #    We can't confirm the binding, but owning_class + ancestors are still real.
    lead, _, rest = key.partition("_")
    if rest and lead in classes:
        return lead, "", rest, "direct_unmatched", "class_prefix"

    return "", "", "", "", ""  # unresolved


def main():
    ours = load_ours()
    sym_idx = load_symbols()
    meth_by_sym, meth_by_pyclass = load_methods()
    classes = load_classes()

    def ancestors(cls):
        return classes.get(cls, {}).get("ancestors", "")

    out_rows = []
    stats = {
        "total": 0, "swig": 0, "swig_resolved": 0,
        "join_c_symbol": 0, "join_python_class_method": 0,
        "join_swig_helper_synth": 0, "swig_unresolved": 0,
        "non_swig": 0,
    }
    cat_counts = {}

    for addr, name in ours:
        stats["total"] += 1
        category = classify(name)
        cat_counts[category] = cat_counts.get(category, 0) + 1

        owning = pyclass = method = binding = join_key = ""
        if name.startswith("swig_"):
            stats["swig"] += 1
            owning, pyclass, method, binding, join_key = enrich_swig(
                name, sym_idx, meth_by_sym, meth_by_pyclass, classes
            )
            if join_key:
                stats["swig_resolved"] += 1
                stats[f"join_{join_key}"] = stats.get(f"join_{join_key}", 0) + 1
            else:
                stats["swig_unresolved"] += 1
        else:
            stats["non_swig"] += 1

        out_rows.append({
            "address": addr,
            "name": name,
            "category": category,
            "owning_class": owning,
            "python_class": pyclass,
            "method": method,
            "binding_kind": binding,
            "ancestors": ancestors(owning) if owning else "",
            "join_key": join_key,
        })

    # ----- write enriched symbol table ------------------------------------- #
    cols = ["address", "name", "category", "owning_class", "python_class",
            "method", "binding_kind", "ancestors", "join_key"]
    with (OUT / "stbc_merged_symbols.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(out_rows)

    # ----- pass through the constant dictionary (address-free, still gold) -- #
    const_src = GE / "stbc_constants.csv"
    const_n = 0
    with const_src.open(encoding="utf-8", newline="") as fin, \
         (OUT / "stbc_constants.csv").open("w", encoding="utf-8", newline="") as fout:
        for i, line in enumerate(fin):
            fout.write(line)
            if i:
                const_n += 1

    # ----- report ---------------------------------------------------------- #
    lines = []
    lines.append("STBC symbol merge report")
    lines.append("=" * 40)
    lines.append(f"location layer  : {OURS}")
    lines.append(f"meaning layer   : {GE}")
    lines.append("")
    lines.append(f"total addressed functions : {stats['total']}")
    lines.append(f"  SWIG wrappers           : {stats['swig']}")
    lines.append(f"    resolved to ABI       : {stats['swig_resolved']}")
    for k in sorted(k for k in stats if k.startswith("join_")):
        lines.append(f"      via {k[len('join_'):]:22s}: {stats[k]}")
    lines.append(f"    unresolved            : {stats['swig_unresolved']}")
    lines.append(f"  non-SWIG (ours-only)    : {stats['non_swig']}")
    lines.append("")
    lines.append(f"constants carried over    : {const_n}")
    lines.append(f"classes available (inheritance) : {len(classes)}")
    lines.append("")
    lines.append("category breakdown (all addressed functions):")
    for cat, n in sorted(cat_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"  {cat:24s} {n}")
    report = "\n".join(lines) + "\n"
    (OUT / "stbc_merge_report.txt").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
