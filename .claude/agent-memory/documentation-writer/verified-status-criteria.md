---
name: verified-status-criteria
description: When a foundation doc qualifies for v5 `verified` status vs `partial` — the threshold and what to do when extrapolation is unavoidable
metadata:
  type: feedback
---

A doc reaches `status: verified` only when **every** evidence row is `confidence: high` or `confidence: medium` with a documented reason. **No `confidence: low` rows.**

**For catalog docs with hundreds of rows, you don't need to decompile every row to qualify for `verified`.** Pattern extrapolation is a valid `confidence: medium` justification when:

1. A representative **sample of at least 6 individual rows** is decompiled and verified.
2. **Sub-cluster spot-checks** (8+ across the full address range) all match the documented pattern.
3. The pattern uniformity itself is documented in the evidence packet as a high-confidence claim.
4. The body table carries a NOTE block calling out which rows are v5-tagged (sampled) vs pattern-extrapolated.

**Why:** Rule (c) from the v5 schema — "`confidence: medium` with a documented reason" — is satisfied by "pattern verified across N samples + M sub-cluster checks; remaining rows extrapolated by uniformity." That's a documented reason. The campaign tracker treats this as documentation debt (a per-row sweep would promote all to `high`) but doesn't block `verified` status.

**Don't conflate medium with low.** Low = pending verification with no evidence. Medium with extrapolation = evidence + a justification. The disposition rule for catalog rows during foundation passes is medium + NOTE, not low + flag.

**Prior catalog doc style decision:** drop, not demote. When a column is systematically wrong (the Guard Flag column in nirtti-factory-catalog had 8/10 wrong), dropping is cleaner than carrying with `confidence: low` markers — because the doc would then have `confidence: low` rows and lose `verified` eligibility. The column has to be load-bearing for the doc family before "keep with low" is worth it.

**How to apply:**
- When the source agent reports "N of M individually verified, M-N extrapolated", check that the pattern is well-evidenced before granting `verified`.
- The NOTE block at the top of the body table is required — it tells the reader which rows to trust at high vs medium confidence.
- Add the open question to the validation log: "a per-row decompile sweep would promote all M-N to high — documentation debt."

**Related:** [[v5-foundation-claim-patterns]], [[catalog-row-disposition-tree]]
