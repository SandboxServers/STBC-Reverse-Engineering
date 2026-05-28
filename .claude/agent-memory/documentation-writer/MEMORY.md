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
