# Ghidra Jython Script: Apply merged symbol names to stbc.exe
# @category STBC
# @description Renames functions at their addresses from the blended symbol
#   table (tools/merged/stbc_merged_symbols.csv) and attaches a plate comment
#   carrying owning_class / ancestors / binding_kind / join_key. This is the
#   "fresh decompilation" seed: run it, then export decompiled C.
#
#   Works in BOTH the GUI Script Manager (with stbc.exe loaded) and headless:
#     analyzeHeadless <proj_dir> <proj> -process stbc.exe \
#         -postScript ghidra_apply_merged_symbols.py <path-to-csv>
#
#   If no CSV path arg is given, falls back to MERGED_CSV_DEFAULT below.
#
# Provenance of the input: tools/merge_symbols.py blends this repo's
# address-anchored function_names_export.txt with the vendored SWIG ABI export
# under tools/abi_export/. See tools/SYMBOLS.md.

import csv
import os

from ghidra.program.model.symbol import SourceType
from ghidra.program.model.listing import CodeUnit

# Edit this if you run from the GUI and don't pass the CSV as a script argument.
MERGED_CSV_DEFAULT = \
    r"C:\Users\mward\Documents\Projects\STBC-Reverse-Engineering" \
    r"\STBC-Reverse-Engineering\tools\merged\stbc_merged_symbols.csv"


def resolve_csv_path():
    args = getScriptArgs()  # noqa: F821 (Ghidra-injected)
    if args and len(args) >= 1 and args[0]:
        return args[0]
    return MERGED_CSV_DEFAULT


def build_comment(row):
    """Compact plate comment from the ABI-enrichment columns (skip empties)."""
    bits = []
    if row.get("category"):
        bits.append("category=%s" % row["category"])
    if row.get("owning_class"):
        bits.append("class=%s" % row["owning_class"])
    if row.get("python_class") and row["python_class"] != row.get("owning_class"):
        bits.append("py_class=%s" % row["python_class"])
    if row.get("binding_kind"):
        bits.append("binding=%s" % row["binding_kind"])
    if row.get("join_key"):
        bits.append("join=%s" % row["join_key"])
    line1 = "  ".join(bits)
    anc = row.get("ancestors") or ""
    if anc:
        return line1 + "\n  ancestors: " + anc.replace("|", " -> ")
    return line1


def main():
    csv_path = resolve_csv_path()
    if not os.path.isfile(csv_path):
        print("[ERR] merged CSV not found: %s" % csv_path)
        return

    fm = currentProgram.getFunctionManager()          # noqa: F821
    af = currentProgram.getAddressFactory()           # noqa: F821
    listing = currentProgram.getListing()             # noqa: F821

    n_total = 0
    n_renamed = 0
    n_same = 0
    n_no_func = 0
    n_bad_addr = 0
    n_err = 0
    n_commented = 0

    fh = open(csv_path, "rb")   # Jython csv wants bytes-mode file handle
    try:
        reader = csv.DictReader(fh)
        for row in reader:
            n_total += 1
            addr_str = (row.get("address") or "").strip()
            new_name = (row.get("name") or "").strip()
            if not addr_str or not new_name:
                n_err += 1
                continue

            # Normalize "0x00609700" -> "00609700" for the address factory.
            hexpart = addr_str[2:] if addr_str.lower().startswith("0x") else addr_str
            try:
                addr = af.getAddress(hexpart)
            except Exception:
                addr = None
            if addr is None:
                n_bad_addr += 1
                continue

            func = fm.getFunctionAt(addr)
            if func is None:
                # Address isn't the entry of a defined function. Rather than
                # invent one, record it; a follow-up pass can create functions.
                n_no_func += 1
                continue

            try:
                cur = func.getName()
                if cur == new_name:
                    n_same += 1
                else:
                    func.setName(new_name, SourceType.USER_DEFINED)
                    n_renamed += 1

                comment = build_comment(row)
                if comment:
                    listing.setComment(addr, CodeUnit.PLATE_COMMENT, comment)
                    n_commented += 1
            except Exception, e:   # Jython 2 syntax
                n_err += 1
                if n_err <= 20:
                    print("[warn] %s @ %s: %s" % (new_name, addr_str, e))
    finally:
        fh.close()

    print("=" * 56)
    print("merged-symbol apply complete")
    print("  rows read           : %d" % n_total)
    print("  functions renamed   : %d" % n_renamed)
    print("  already correct     : %d" % n_same)
    print("  plate comments set  : %d" % n_commented)
    print("  addr not a function : %d" % n_no_func)
    print("  bad address         : %d" % n_bad_addr)
    print("  errors              : %d" % n_err)
    print("=" * 56)


main()
