# FINAL_NAMING_QC — IONE naming alignment and submission QC

Date: 2026-10-12. Branch: `devin/179179158-ione-naming` (post-merge #11).
Fixed expansion: **IONE = Identifiability-Oriented Navigation of Evidence**.

## Changes

| file | change |
|---|---|
| `paper/paper.md` | title set to exact approved string; Summary opens "IONE (Identifiability-Oriented Navigation of Evidence) is an open-source Python package …"; legacy mention explicitly labeled "original/legacy IONE (Incoherence-Oriented Neutralisation and Extraction)" |
| `README.md` | rewritten: current product first; legacy README moved to `docs/legacy_ione.md` with historical banner; legacy section kept, labeled |
| `docs/legacy_ione.md` | original README preserved verbatim after banner — historical mentions of the old expansion NOT rewritten |
| `CITATION.cff` | title = "IONE: Identifiability-Oriented Navigation of Evidence" |
| `pyproject.toml` | description updated; package `ione`, dist `ione-audit`, CLI `ione` unchanged |
| `ione/__init__.py` | docstring expansion updated |
| `docs/aggregate_audit/README.md` | header uses new expansion |
| `paper/paper.bib` | legacy bib title labeled original/legacy |

NOT changed (by design): import path `ione`, CLI `ione`, repository
URL/name, `results/manuscript/*` historical documents (all Incoherence
mentions remain as history), scientific results, verdict semantics.

## Consistency checks

- `grep Incoherence` outside `results/` now hits only explicitly-labeled
  legacy contexts (README legacy section, `docs/legacy_ione.md`,
  paper.md legacy note).
- No API/CLI/behavior change; verdicts still conditional LP bounds;
  augmentation still non-guaranteed; borrow check still retrospective.

## Verification

- `python3 -m pytest tests/` → **27/27 pass** (0.23 s).
- `ione audit --study recovery --target noO2` → REVERSIBLE,
  RD ∈ [-1.000, +0.959], solver status 0.
- `pip install .` verified earlier on this branch's base (pip ≥24
  required — noted in DECISION.md).
- GitHub Actions `tests.yml`: pytest matrix 3.9/3.11/3.12 all PASS on
  this branch (verified via PR checks).

## JOSS author-instruction check

- Verified 2026-10 against joss.readthedocs.io: requirements are OSI
  license, research application, feature-complete software, docs,
  paper.md + bibliography, AI-use disclosure. No codified ≥6-month
  public-history rule was found in the current official text.
- Public-start date: **UNVERIFIED** (git timestamps ≠ public visibility).

## Remaining author actions (non-blocking)

1. Confirm affiliation English form + supply ORCID (paper.md has no
   ORCID — flagged, not invented).
2. Review `paper/paper.md` draft; approve any submission.
3. Decide on release tag/version after merge.
4. Optional: JOSS pre-submission eligibility inquiry for public-history
   evidence.

## Verdict: **GO** for submission-readiness QC

All acceptance criteria met: exact expansion consistent across title,
Summary, README, citation metadata; legacy naming preserved as labeled
history; interfaces and statistical behavior unchanged; 27/27 tests
pass; limitations transparent.
