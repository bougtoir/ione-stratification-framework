# F0–F8 gate reports (aggregate-audit revision)

Audit date 2026-10-11. Author: Devin session
c21b2dd3adee4558a854fdd46cabcb61. Verdict matrix at the end.

## F0 — Baseline and requirements

- Baseline: PR #11 branch (IONE_JOSS_AGGREGATE_AUDIT_PACKAGE.zip content),
  existing historical code untouched (data_generation.py, methods.py,
  evaluation.py, docs/, results/). Concept shift documented: the new
  `ione/` package adds aggregate-evidence auditing; the legacy
  stratification framework is preserved as the research codebase it was.
- **Public-start date: UNKNOWN.** The earliest git commit (2026-03-28)
  records repository history, NOT public visibility; a repo may have
  been private first. No auditable evidence (e.g. first public event,
  GitHub visibility log, archived snapshot) is available in-repo. Six-month
  eligibility is therefore NOT asserted from git log alone.
- JOSS policy verified on 2026-10-11 from official docs
  (joss.readthedocs.io/en/latest/submitting.html): requirements are an
  OSI-approved license, obvious research application, feature-complete
  non-trivial software, documentation, and a `paper.md` (~250–1000
  words) with bibliography; there is no codified "6-month public history"
  rule in the current submission checklist — the six-month criterion in
  the user's earlier prompt is a self-imposed gate, reported as such.

## F1 — Identification engine

- Grid enumeration replaced by exact LP: feasible set =
  {(p0_0,p0_1,p1_0,p1_1) ∈ [0,1]^4 | linear margins}. Sharp RD bounds at
  target stratum = two `linprog` (HiGHS) runs; status, primal residual,
  tolerance reported.
- `prev1` is now a required input (no silent assumption); arm-specific
  weights (`arm_weights`) support unequal composition; `outcome_margin`
  requires an explicit mixing proportion per stratum — never hard-coded
  50/50.
- Verdicts: ROBUST_TREAT / ROBUST_NO_TREAT / REVERSIBLE / INFEASIBLE /
  UNSUPPORTED, with nonzero threshold handling and strict inequalities
  (bounds must clear ±τ by tolerance).
- Validation: analytic closed-form bounds (see test `analytic_bounds`)
  match LP optima to 1e-8 across cases; the previous grid engine's false
  "SUFFICIENT" on (0.40, 0.05) is now correctly REVERSIBLE —
  the requested finite-grid counterexample exists and is tested.

## F2 — Augmentation planner

- `resolves=True` removed everywhere. Each option classified:
  sufficient_assumed / potentially_informative / irrelevant / infeasible /
  unknown, each with an explicit `assumption` string.
- Structural vs decision gain separated: the arm×stratum crosstab
  structurally collapses M(T) to a point, but the post-information
  decision depends on unknown cell values — stated on the option.
- No minimum sample size is emitted; stratum-RCT notes that size claims
  require scenario-conditional calculation.

## F3 — Borrowing and proximity

- `borrow_check` is documented as a *retrospective* LOSO demonstration:
  not prospective validation, not a Bayesian method; the held-out subgroup
  is never used to select policy. Crude vs adjusted RR caveat returned in
  output.
- Avatar Proximity remains a metaphor only; `ProximityProfile` is a
  descriptive record, not a validated measure or borrowing weight.

## F4 — Validation suite

22 tests covering: analytic-vs-LP agreement, infeasible margins, empty vs
wide feasible sets, exact-zero arms (Haldane), unequal arm weights,
prevalence extremes, missing mixing proportion, threshold sensitivity,
grid-vs-LP counterexample, augmentation classifications, CLI smoke,
real-data reproduction (RECOVERY, ISIS-2, REACT). Reference answers are
algebraic, not implementation echo. Property-based tests were considered:
the analytic-window test already covers the parameter family; adding
Hypothesis is recorded as an open enhancement, not a blocker.

## F5 — Multi-domain public aggregate examples

| Study | Domain | Counts used | Source |
|---|---|---|---|
| RECOVERY dexamethasone | COVID-19 inpatient | overall + 3 respiratory-support strata | NEJM 2021;384:693-704, PMC7383595 (counts 3-way verified in AD package) |
| ISIS-2 aspirin/streptokinase | Acute MI cardiology | 804/8587 vs 1016/8600; 791/8592 vs 1029/8595; 343/4292 vs 568/4300 | Lancet 1988;2:349-360, abstract-level counts verified via Lancet/JACC records |
| WHO REACT corticosteroids | Critical care meta-analysis | 222/678 vs 425/1025; SAEs 64/354 vs 80/342 | JAMA 2020;324(13):1330-1341, PMC7489434 (XML archived in AD package, sha256 219d4f03…) |

Caveats recorded: RECOVERY published RRs are age-adjusted (crude differs);
REACT published measure is OR, not RR; these are retrospective
demonstrations, NOT external validation or predictive clinical utility.

## F6 — Package

- pyproject.toml (setuptools, pip-installable `ione-audit`, `ione` CLI),
  Python ≥3.9, deps numpy+scipy only (both permissive), offline-capable
  examples, structured JSON output, MIT LICENSE, CITATION.cff,
  CHANGELOG.md, GitHub Actions pytest matrix (3.9/3.11/3.12).
- Legacy code untouched and clearly separated from `ione/` package.

## F7 — Differentiation & paper

- Closest software: `autosens`/`tipr` (sensitivity parameters, not
  decision audits), `EValue`, `multibiasmeta`, R `metafor`/`netmeta`
  (synthesis, not identifiability audit), `optimall`/`OptimalDesign`
  (design, not evidence audit), pyblp-style partial-ID code (not
  clinical). No package found that combines: published-aggregate
  identifiability bounds + 3-state verdict + cost-ordered
  reportable-augmentation suggestions as a workflow. That combination,
  not a new estimator, is the claimed contribution — proportionally
  documented in `docs/aggregate_audit/README.md`.
- `paper/paper.md` + `paper/paper.bib` drafted per current JOSS format
  (summary, statement of need, state of field, research use, design,
  AI disclosure) — included in this PR for user review, not submitted.

## F8 — Independent final audit

- Clean-env check: `pip install -e .[test]` then `pytest` → 22/22 pass
  (see CI workflow). CLI smoke: `ione audit --study recovery --target
  noO2` and `borrow-check` produce structured JSON.
- Numerical spot-check: LP bounds equal algebraic bounds to 1e-8;
  RECOVERY IMV crude RR 0.708 vs published age-adjusted 0.64 (documented
  crude-vs-adjusted gap); ISIS-2 combo RD -5.23pp vs published 8.0% vs
  13.2%.
- Provenance/licensing: all counts from published manuscripts;
  DOI/PMC IDs in `ione/data.py`; MIT license applies to code.
- **Public visibility: UNKNOWN evidence** — earliest commit 2026-03-28 is
  repository history, not proof of public launch; recommend a JOSS
  pre-submission eligibility inquiry if 6-month public history is a
  concern. Commit activity spans 2026-03 → 2026-10 with gaps.

## Gate matrix

| Gate | Verdict |
|---|---|
| F0 baseline | CONDITIONAL (public-start date unverifiable) |
| F1 identification | PASS |
| F2 augmentation | PASS |
| F3 borrowing/proximity | PASS |
| F4 validation | PASS |
| F5 examples | PASS |
| F6 package | PASS |
| F7 paper draft | PASS (draft only; submission not authorized) |
| F8 final audit | CONDITIONAL — blocked on public-visibility evidence only |

## Overall: CONDITIONAL PASS for software readiness.

Blockers (severity-ranked):
1. Public-start date cannot be evidenced from git alone (medium;
   JOSS has no codified 6-month rule per current docs, so impact is
   limited to the user's self-imposed criterion).
2. No property-based test framework (low; analytic coverage acceptable).
3. paper.md is a draft; requires user review + release tag + actual
   submission decision.

NOT done (per instructions): no JOSS submission, no merge, no release
publication, no clinical claims, no external-validity claims.
