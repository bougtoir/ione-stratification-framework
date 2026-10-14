# Gate A1 — AJS適合性（一次情報の検証済み規定）

Verified 2026-10-13 (UTC) against live sources:
- https://www.ajs.or.at/index.php/ajs/about/submissions (Author Guidelines,
  Submission Preparation Checklist, Copyright Notice)
- https://www.ajs.or.at/index.php/ajs/about (About the Journal: aims,
  refereeing policy, publication ethics)
- https://github.com/matthias-da/ajs-public (official `ajs.cls`, `ajs.bst`,
  `template-guidelinesAJS.tex` — cloned and read in full)

## Journal identity

- Austrian Journal of Statistics (AJS), journal of the Austrian
  Statistical Society (Österreichische Statistische Gesellschaft).
  5–7 issues/year. Open access; indexed in Scopus (per journal site).
- Scope (aims page): "promote and extend the use of statistical methods
  in all kinds of theoretical and applied disciplines" — publishes
  computational statistics, statistical software, and applied work.

## Verified requirements

| item | rule | evidence |
|---|---|---|
| Fees | **No submission fee, no processing fee, no publication fee** ("The refereeing and publishing ... is free of charge") | submissions page; about page |
| License / copyright | CC-BY; **authors retain copyright**, grant license to publish | submissions page Copyright Notice |
| Format | **LaTeX strongly required** — "Papers not considering our style might be automatically rejected"; official `ajs.cls` template (JSS-derived). Word only rarely, at exceptional quality | submissions page; guidelines §C1.word |
| Template | `github.com/matthias-da/ajs-public` (also Overleaf) | cloned 2026-10-13 |
| Figures | **PDF vector graphics only** — no png/jpeg, no converted pixels; embedded at appropriate points in text, not at end | checklist; guidelines §C2.graphics |
| Tables | produced in LaTeX (no screenshots) | guidelines §C2.tables |
| Title style | title capitalized (title case); section/subsection headers non-capitalized | checklist; §C2 |
| References | author-date style via `ajs.bst`; **all cited papers' titles in title case**; include DOI where possible; full author lists acceptable | §C2.references; checklist |
| Software citation | software used must be cited ("to not cite software is plagiarism") | checklist |
| Submission file | PDF uploaded through editorial system at ajs.or.at (registration required) | §Submission; checklist |
| Review | anonymously refereed | about page |
| Prior submission | must not be under consideration elsewhere; **author should notify if an earlier version was submitted before** — JOSS history will be disclosed in cover letter/Comments | about page |
| Reviewer suggestions | **optionally** names/addresses of ≥3 potential reviewers with manuscript | checklist |
| Data/code | "considered to place used and analyzed data at disposal for the referees"; reproducible files (knitr/markdown) accepted; supplementary code encouraged | about page; guidelines |
| Average time to publication | ≈132 days (guidelines FAQ) | guidelines |
| Abstract/keywords | `\Abstract`, `\Keywords` (≥1), `\Address` at end | ajs.cls usage |

## Fit assessment

- AJS regularly publishes statistical-software papers with worked
  applications (recent examples located: "circlus: An R Package for
  Circular and Spherical Clustering" 2025; "lionfish" interactive
  visualization 2025; flex-scheme ordinal clustering 2025). An audited
  Python package paper with three real trial-data applications is within
  normal AJS scope.
- Known desk-reject traps to satisfy explicitly: LaTeX format, a real
  Discussion/Conclusion comparing to alternative methods, sufficient
  data documentation, non-toy applications (our applications are three
  landmark RCTs/meta-analyses — not toy data).
- JOSS's community/development-history criteria do NOT transfer to AJS;
  nothing in AJS rules requires ≥N months public history.
- Unclear/not verified: exact word limit (none stated), running-head
  length (none stated — 46-char rule does not apply here), ORCID
  requirement (orcidlink optional in template).

## Implications for A4

- Write in LaTeX with ajs.cls directly (template cloned to
  `ajs/template/`); bibtex `ajs.bst`, author-date citations.
- All figures as PDF; tables as LaTeX; everything cited in order.
- Cover letter notes the JOSS history (fair-notification rule).
- Prepare optional reviewer suggestion list (real people, verifiable
  affiliations — flagged for user approval before any submission).
