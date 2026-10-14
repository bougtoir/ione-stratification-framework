# Gate A5 — Editorial fit audit (AJS)

## Fit with AJS aims and current content

AJS's stated objective is to "promote and extend the use of statistical
methods in all kinds of theoretical and applied disciplines" and it
routinely publishes statistical-software-with-application papers
(recent examples: circlus R package, lionfish, flex-scheme clustering).
The IONE paper is exactly this genre: a tested Python package solving a
concrete applied-statistics problem (what published aggregate RCT data
identify about subgroup decisions), with three real applications and
vector figures/tables in the house style.

## Desk-reject risk audit (AJS's own checklist)

| AJS checklist item | status |
|---|---|
| PDF upload via editorial system | ready (9 pp, compiled) |
| AJS style (ajs.cls, ajs.bst, author-date, title case) | used; template cloned from official repo 2026-10-13 |
| Vector (PDF) figures only | yes — both figures are vector PDFs |
| Title capitalized; headers non-capitalized | yes |
| Reference titles in title case + DOIs | yes — all 18 bib entries title-cased with DOI where it exists |
| LaTeX tables (no screenshots) | yes (booktabs) |
| Software cited (NumPy, SciPy, HiGHS) | yes |
| ≥3 reviewer suggestions | optional; prepared candidates (see checklist) |
| Conclusion/Discussion present, compares to alternatives | yes (Sections 5–6) |
| Data documentation sufficient | Table 1 + provenance paragraph |
| Non-toy applications | 3 landmark trials/meta-analysis |
| Prior submission disclosed | cover letter states JOSS history (per AJS fairness rule) |

## Adversarial novelty check

Could a referee say "nothing new"? The math (marginal-consistency LP)
is classical and we say so, citing Cross & Manski 2002, King 1997, and
the concurrent Moon 2026. The defensible contribution for AJS is: (i) a
complete audit workflow tuned to published clinical-trial reports
(consistency screen → bounds → disjoint verdicts → ordered
reportable augmentations), (ii) the real-data demonstration that
published subgroup margins are usually decision-reversible, and
(iii) the documented borrow-check reversal. This is a software/applied
contribution, which AJS publishes; the manuscript frames it as such and
does not claim new theory. Risk: moderate — mitigated by honest framing.

## Social value (A5_SOCIAL_VALUE.md content, folded in)

- Who benefits: clinical researchers and evidence synthesists without
  IPD access; trial groups receiving concrete minimal re-tabulation
  requests; teachers of identification vs estimation.
- The message delivered: "not identifiable" becomes "here is exactly
  what the margins identify and the cheapest thing that would resolve
  it" — a concrete next step instead of a dead end.
- No treatment recommendations are made; abstention is a first-class
  output.
