# Documentation Writer — Memory

Cross-session notes on STBC doc style, the doc-index map, and patterns that work for this codebase.

## Index

Entries appear here as the campaign progresses. Each entry links to a topic file in this directory; this index stays under 200 lines.

- [v5 named-function convention](v5-named-function-convention.md) — how to demote pre-v5 annotation-script names in catalog docs without dropping the addresses
- [v5 foundation claim patterns](v5-foundation-claim-patterns.md) — evidence-row patterns for totals, address ranges, and exhaustive partitions in foundation-tier docs
- [catalog row disposition tree](catalog-row-disposition-tree.md) — four-bucket decision tree (keep / keep-as-is / move to internal-only / drop) for pre-v5 catalog rows during re-validation
- [verified status criteria](verified-status-criteria.md) — when a foundation doc qualifies for `verified` vs `partial`; pattern extrapolation as a valid medium-confidence justification
- [vtable doc render patterns](vtable-doc-render-patterns.md) — 4 patterns for vtable reference docs: address reassignment, two-stage construction, GetRTTI cross-check, vtable-size vs object-size disambiguation
- [TG vtable render patterns](tg-vtable-render-patterns.md) — 5 TG-specific patterns: __purecall reclassification, universal slot inheritance, type-ID constants table, sibling cross-link section, zero-xref negative claim format
- [process-meta doc pattern](process-meta-doc-pattern.md) — process-meta docs (coverage reports, pass narratives) validate by content removal, not address re-anchoring; three-class section taxonomy + status-partial-not-verified rule
- [cross-source doc render patterns](cross-source-doc-render-patterns.md) — two-tag convention ([v5-validated] for stbc.exe vs [cross-source-YYYY-MM-DD] for external corpora); intro NOTE block; address:null + file:line in note for external-corpus evidence rows
- [leaf doc render patterns](leaf-doc-render-patterns.md) — 8 patterns for leaf docs (event system, UI hierarchy): dropped-name NOTE block, anchored-vs-inferred methodology, universal-slot disclosure, indirection diagrams, dual sub-struct tables, Two-RTTI-Systems disclosure, partial-not-verified rule for corrections, Open-Questions debt list
- [load-bearing correction disambiguation](load-bearing-correction-disambiguation.md) — pattern for "two distinct globals were conflated" corrections: dedicated disambiguation subsection near doc top, two-row table, flag CLAUDE.md batch correction in body, cross-doc impacts in tracker
