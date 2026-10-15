# P3 Technical Manuscript Baseline Audit

Status: `P3-G0 — TECHNICAL BLUEPRINT ONLY`

Scientific source lock: `3f6e5302483681209e2408531eb5a15389f9fded`
Transformation version: `p3-g0-builder-v1`

## Scope and method

Both supplied historical DOCX files were opened read-only, exported through Microsoft Word to PDF, rasterized at 100 DPI and visually reviewed on every rendered page (33 + 13 pages). Structural checks used OOXML/python-docx plus the bundled heading, field, section, image, table-geometry, style, accessibility, comments and footnote audit helpers. LibreOffice was unavailable on PATH, so the fallback export route is disclosed. Neither DOCX was edited.

## Baseline 1 — five-chapter report

`DeFiStress_BAO_CAO_NCKH_HOAN_CHINH.docx` has SHA-256 `9c8486027efcd35fe8fbcb8ba4c9fd6cfb714d2785f40ca6a64c247627dceb96`, 33 rendered pages, 3 sections, 349 body paragraphs, 22 tables and 16 inline images. Heading styles are present (5/40/12 at levels 1/2/3), and the visible structure is five chapters plus front matter, references and appendices.

- A live TOC field and PAGE field exist; no SEQ caption fields, REF cross-reference fields, LOT/LOF fields or bookmarks were found.
- Thirty-one `Caption`-style and 31 `Nguồn`-style paragraphs are plain text. They are not field-backed numbering/cross-references.
- No OMML equation objects were found; displayed formulas are text/direct formatting.
- No comments, tracked insertions/deletions, footnotes or endnotes were found.
- The accessibility audit reports 16 high findings (all inline images lack alt text) and 22 medium findings (table header rows are not marked). The table geometry helper reports 229 structural width/indent/grid findings.
- Visual review found no gross clipping or unreadable overlap, but page 33 is nearly empty except for the tail of the reproducibility paragraph, indicating an avoidable pagination/orphan issue.
- The manuscript contains pre-lock numerical narratives: the original 32-cell grid conclusion and a 0/200 Monte Carlo table conflict with the locked version precedence. Those tables/figures must not be reused without rebuilding from locked evidence.

## Baseline 2 — introduction/literature proposal

`DeFi_Stress_Lab_Mo_Dau_Tong_Quan_Nghien_Cuu.docx` has SHA-256 `582d489189a156f00a563d22b6db36caab8094d7a3581d220b96d8b3f1aebdd5`, 13 rendered pages, 1 section, 106 body paragraphs and 8 tables. It has 11 Heading 1 and 12 Heading 2 paragraphs.

- It has a PAGE field but no TOC, SEQ, REF, LOT/LOF, bookmark or OMML equation structures.
- The visual flow is readable and consistent, but the file is a proposal/introductory baseline rather than the locked seven-chapter manuscript.
- Four tables lack marked header rows. The table geometry helper reports 36 structural findings.
- No comments or tracked changes were found.

## Existing research figures/tables

The repository contains legacy `A01–A22`, `T01–T12`, `C01` and other pre-lock outputs. Presence is not sufficient provenance. Only artifacts resolved through Final Accepted Claims Registry v1.1, its active result IDs and locked source locators are eligible for the proposed P3 catalog. Existing Frozen v3 figures F01–F04 may be reused only after caption/policy/denominator review.

## Technical gaps before manuscript production

1. Work has not yet supplied the Commander-approved seven-chapter blueprint, so no exhibit is assigned to a final chapter or section.
2. No official school template was provided or verified. The two historical DOCX files are not treated as template truth.
3. Caption numbering, cross-references, LOT and LOF need a field-backed Word implementation in a later approved stage.
4. Figure alt text, table header semantics and table geometry need remediation in the final manuscript, not in these read-only source files.
5. Equations require a consistent OMML/Word-equation workflow; current baselines use plain text.
6. Bibliography formatting is visually present but was not treated as authoritative because P2 literature files, not these DOCX files, are the locked scholarly source.

## G0 conclusion

The historical five-chapter manuscript is useful only as a layout/content baseline. It is numerically superseded in material places and cannot serve as the P3 evidence source. School-template compliance remains `NOT_VERIFIED — TEMPLATE_NOT_PROVIDED`.

Content SHA-256 (UTF-8, excluding this checksum line): `6fb521191648d068eb888e74f4e3891c255f3ffd67c058cb1d823eb1d9623dd8`
