# Page-by-page visual QC — ione_ajs.pdf (final build)

Rendered every page at 150 dpi (pdftoppm) and inspected at full size.
Checker: Devin, 2026-10-14. Baseline renders (pre-fix) and final renders
(post-fix) both audited; pages whose layout did not change between
builds were re-verified on the final render where indicated.

| p. | Contents | Verdict | Notes |
|----|----------|---------|-------|
| 1 | Title, authors, abstract, keywords, §1 start | PASS | journal header/logo inside bounds (V-05 template exception, no visual defect) |
| 2 | Introduction, prior work, contributions | PASS | clean margins, citations wrap correctly |
| 3 | §2 data/estimand, equations (1), bounds, verdicts start | PASS | equations inside margins, bullet list fine |
| 4 | verdict list cont., §2.3 levels, §2.4–2.5 | PASS | L1/L2/L3 itemize clean, no widow issues |
| 5 | §2.5 cont., §2.6, §3 implementation, §4 start | PASS (fixed) | V-02 resolved: API list breaks after `audit_decision`; `sloppypar` localized to this paragraph only |
| 6 | Table 1, Table-2 lead-in, RECOVERY/ISIS-2/REACT paragraphs | PASS (fixed) | V-01 resolved: table and both footnotes inside margins |
| 7 | Table 2, Figure 1, borrow-check text, §5 start | PASS (fixed) | V-03/V-04 resolved: annotation fully inside axes; vector figure, Type-42 font |
| 8 | §5.1–5.4, §6 conclusions start | PASS | clean |
| 9 | conclusions end, References start | PASS | DOIs wrap via cls `\doi` macro; no overfull entries |
| 10 | references end, affiliation block, journal footer | PASS | V-07 template exception: cls footer block, visually fine |

Machine-assisted checks: `pdftotext` extraction confirms text is
searchable/selectable; `pdffonts` shows all fonts embedded, zero Type 3
(final). Overfull warnings remaining: only the three cls-template cases
recorded as exceptions above; all were cross-checked against the
rendered page and show no visible defect.
