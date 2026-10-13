# Gate A6 — AJS submission checklist

Date: 2026-10-13 (UTC). Manuscript: `ajs/manuscript/ione_ajs.pdf` (9 pp,
AJS style, compiled from `ione_ajs.tex` + `ione_ajs.bib`).

## Package contents

- `ione_ajs.tex`, `ione_ajs.bib`, `ione_ajs.pdf` — manuscript (AJS
  `ajs.cls`/`ajs.bst`, author-date, title-case titles/references).
- `fig_bounds_vs_q.pdf`, `fig_verdicts.pdf` — vector figures.
- `cover_letter.md` — cover letter (I-voice, discloses JOSS history).
- `ajs/analysis/reproduce_a3.py` — reproduces every number/table/figure.
- `ajs/audit/` — A0–A6 audit documents, CSVs, logs.

## Compliance checks performed

- [x] LaTeX in official AJS style; compiles clean (no unresolved refs;
      masthead overfull is a template artifact also present in the
      official template itself).
- [x] Figures vector PDF, embedded in text, cited in order; tables in
      LaTeX, cited in order (Table 1 before Table 2; Figure 1 before 2).
- [x] Title/section capitalization per checklist; references title case
      with DOIs.
- [x] Software cited: NumPy, SciPy, HiGHS (AJS plagiarism rule).
- [x] Numbers consistent across abstract/text/tables with CSV outputs
      (bounds [-1.000,+0.959] etc. verified against a3_verdicts.csv).
- [x] AI-assistance disclosure: recommended to add per author policy —
      the JOSS paper carried one; equivalent line added to cover letter
      context (manuscript states verification regime).
- [x] No APC/fee — verified "no submission, processing, or publication
      fee"; CC-BY; authors retain copyright.
- [x] Prior submission disclosure in cover letter (AJS fairness rule).
- [ ] ORCID for author — **unverified** (author action).
- [ ] Affiliation official English name — used "Shiga University, Data
      Science AI Innovation Research Promotion Center" per prior naming
      package; **author to confirm** + postal address currently guessed
      as Shiga University, Hikone — author to confirm.
- [ ] Optional reviewer suggestions (≥3): candidate pool prepared —
      Tom M. Palmer (MRC IEU, Bristol; bpbounds author), Ilya Shpitser
      (Johns Hopkins; causal inference/partial ID), Maya B. Mathur
      (Harvard/Stanford; sensitivity analysis). Affiliations verifiable
      from public pages; no email addresses invented — provide only
      after author confirms no conflict of interest.

## Not done (per instructions)

- No submission, no merge, no release tag. All await user approval.
