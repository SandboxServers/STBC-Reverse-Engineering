//Apply merged symbol names to stbc.exe from tools/merged/stbc_merged_symbols.csv.
//Renames each function at its address and attaches a plate comment carrying
//owning_class / ancestors / binding_kind / join_key. Java version so it runs in
//stock Ghidra with no Jython/PyGhidra. Run from Script Manager (category STBC).
//@category STBC
//@author STBC-RE
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.symbol.SourceType;

public class ghidra_apply_merged_symbols extends GhidraScript {

    // Fallback if the CSV can't be located next to the script and no arg given.
    private static final String CSV_DEFAULT =
        "C:\\Users\\mward\\Documents\\Projects\\STBC-Reverse-Engineering"
      + "\\STBC-Reverse-Engineering\\tools\\merged\\stbc_merged_symbols.csv";

    private File resolveCsv() {
        String[] args = getScriptArgs();
        if (args != null && args.length >= 1 && args[0] != null && !args[0].isEmpty()) {
            return new File(args[0]);
        }
        // Prefer the copy next to this script: <tools>/merged/stbc_merged_symbols.csv
        try {
            File toolsDir = getSourceFile().getParentFile().getFile(false);
            File beside = new File(toolsDir, "merged/stbc_merged_symbols.csv");
            if (beside.isFile()) {
                return beside;
            }
        } catch (Exception e) {
            // fall through to default
        }
        return new File(CSV_DEFAULT);
    }

    // Split a CSV line into exactly the header's field count. Our fields never
    // contain commas (identifiers, class names, and '|'-separated ancestors),
    // so a plain split is safe.
    private String[] fields(String line, int n) {
        String[] parts = line.split(",", -1);
        if (parts.length < n) {
            String[] padded = new String[n];
            System.arraycopy(parts, 0, padded, 0, parts.length);
            for (int i = parts.length; i < n; i++) padded[i] = "";
            return padded;
        }
        return parts;
    }

    private String buildComment(String category, String owning, String pyClass,
                                String binding, String ancestors, String joinKey) {
        StringBuilder sb = new StringBuilder();
        if (!category.isEmpty()) sb.append("category=").append(category).append("  ");
        if (!owning.isEmpty())   sb.append("class=").append(owning).append("  ");
        if (!pyClass.isEmpty() && !pyClass.equals(owning))
            sb.append("py_class=").append(pyClass).append("  ");
        if (!binding.isEmpty())  sb.append("binding=").append(binding).append("  ");
        if (!joinKey.isEmpty())  sb.append("join=").append(joinKey);
        String line1 = sb.toString().trim();
        if (!ancestors.isEmpty()) {
            return line1 + "\n  ancestors: " + ancestors.replace("|", " -> ");
        }
        return line1;
    }

    @Override
    public void run() throws Exception {
        File csv = resolveCsv();
        if (!csv.isFile()) {
            println("[ERR] merged CSV not found: " + csv.getAbsolutePath());
            return;
        }
        println("reading " + csv.getAbsolutePath());

        FunctionManager fm = currentProgram.getFunctionManager();
        Listing listing = currentProgram.getListing();

        int nTotal = 0, nRenamed = 0, nSame = 0, nCommented = 0, nCreated = 0;
        int nNoFunc = 0, nBadAddr = 0, nErr = 0;

        BufferedReader br = new BufferedReader(new FileReader(csv));
        try {
            String header = br.readLine(); // skip header
            if (header == null) {
                println("[ERR] CSV is empty");
                return;
            }
            String line;
            while ((line = br.readLine()) != null) {
                if (line.trim().isEmpty()) continue;
                nTotal++;
                if (monitor.isCancelled()) break;

                String[] f = fields(line, 9);
                String addrStr  = f[0].trim();
                String name     = f[1].trim();
                String category = f[2].trim();
                String owning   = f[3].trim();
                String pyClass  = f[4].trim();
                String binding  = f[6].trim();
                String ancestors= f[7].trim();
                String joinKey  = f[8].trim();

                if (addrStr.isEmpty() || name.isEmpty()) { nErr++; continue; }

                String hex = addrStr.toLowerCase().startsWith("0x")
                           ? addrStr.substring(2) : addrStr;
                Address addr;
                try {
                    addr = toAddr(hex);
                } catch (Exception e) {
                    addr = null;
                }
                if (addr == null) { nBadAddr++; continue; }

                Function func = fm.getFunctionAt(addr);
                boolean created = false;
                if (func == null) {
                    // Not yet a defined function -- typical for SWIG wrappers /
                    // NiRTTI factories only reached via data pointer tables.
                    // Disassemble the bytes and carve out a function here.
                    try {
                        disassemble(addr);
                        func = createFunction(addr, name);
                    } catch (Exception e) {
                        func = null;
                    }
                    if (func == null) { nNoFunc++; continue; }
                    created = true;
                    nCreated++;
                }

                try {
                    if (created) {
                        // name already set by createFunction; nothing to rename
                    } else if (func.getName().equals(name)) {
                        nSame++;
                    } else {
                        func.setName(name, SourceType.USER_DEFINED);
                        nRenamed++;
                    }
                    String comment = buildComment(category, owning, pyClass,
                                                  binding, ancestors, joinKey);
                    if (!comment.isEmpty()) {
                        listing.setComment(addr, CodeUnit.PLATE_COMMENT, comment);
                        nCommented++;
                    }
                } catch (Exception e) {
                    nErr++;
                    if (nErr <= 20) println("[warn] " + name + " @ " + addrStr + ": " + e);
                }
            }
        } finally {
            br.close();
        }

        println("========================================================");
        println("merged-symbol apply complete");
        println("  rows read           : " + nTotal);
        println("  functions renamed   : " + nRenamed);
        println("  functions created   : " + nCreated);
        println("  already correct     : " + nSame);
        println("  plate comments set  : " + nCommented);
        println("  addr not carvable   : " + nNoFunc);
        println("  bad address         : " + nBadAddr);
        println("  errors              : " + nErr);
        println("========================================================");
    }
}
