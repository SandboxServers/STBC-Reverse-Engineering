# STBC symbol datasets

Three layers of symbol intelligence for `stbc.exe`, plus a script that blends
them into one enriched table.

## Inputs

| Path | Layer | Rows | Has addresses? |
|------|-------|------|----------------|
| `function_names_export.txt` | **location** — `address,name` | 4,981 | yes |
| `abi_export/stbc_symbols.csv` | **meaning** — `c_symbol → owning_class, method, binding_kind` | 2,865 | no |
| `abi_export/stbc_methods.csv` | full `python_class.method → c_symbol` join (incl. Ptr twins) | 36,538 | no |
| `abi_export/stbc_classes.csv` | inheritance graph — `class, is_ptr, direct_bases, ancestors` | 630 | no |
| `abi_export/stbc_constants.csv` | valued constants (opcodes/enums) — `name, hex, dec, value_repr` | 3,831 | no |

The `abi_export/` CSVs are **vendored** from the open_stbc repo
(`tools/probes/results/ghidra_export/`, built by `build_ghidra_export.py` from
the q13 console-probe dumps of the SWIG PyMethodDef table). See
`abi_export/UPSTREAM_README.md` for the upstream schema notes and Ghidra flow.
They carry no addresses — the location layer supplies those.

## Blend

```bash
# any Python 3, stdlib only:
/c/projects/open_stbc/.venv/Scripts/python.exe tools/merge_symbols.py
# refresh from a fresh upstream export without re-vendoring:
ABI_EXPORT=/c/projects/open_stbc/tools/probes/results/ghidra_export \
  python3 tools/merge_symbols.py
```

`merge_symbols.py` keys each addressed SWIG symbol onto the ABI export through a
cascade of join strategies (exact `c_symbol`, `python_class_method`, ctor/dtor,
field accessor, helper synth, class-prefix fallback) and passes the constant
dictionary through untouched.

## Outputs — `tools/merged/`

- **`stbc_merged_symbols.csv`** — one row per address:
  `address, name, category, owning_class, python_class, method, binding_kind, ancestors, join_key`
- **`stbc_constants.csv`** — the 3,831 valued constants (address-free; for the
  packet decoder / immediate labelling).
- **`stbc_merge_report.txt`** — match/residual accounting.

### Current coverage (4,981 addressed functions)

- **3,967 / 3,976** SWIG wrappers resolved to ABI semantics (owning class +
  inheritance chain).
- **1,005** non-SWIG "ours-only" internals preserved and tagged
  (`nirtti_factory`, `re_dispatcher_handler`, `engine_internal`, ctors, dtors,
  vtable fns) — these have no ABI-export counterpart because they are not
  Python-scriptable.
- **9** truly unresolved: module-level free functions with no class prefix
  (`swig_BreakIntoSets`, `swig_Breakpoint`, …). Nothing to join them against.

The `join_key` column records how each row was resolved, so residuals and
lower-confidence rows (`class_prefix`, `direct_unmatched`) are auditable.
