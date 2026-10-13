# Gate A0 — Input freeze & implementation audit

Date: 2026-10-13 (UTC). Working branch `devin/1791902572-ione-ajs`.
Canonical code snapshot: commit `21a253ee93e7e25833a95afeed2469865b41a609`
(head of merged PR #12 `devin/179179158-ione-naming`).

## 1. Discrepancy found at input freeze (important)

The handoff states "main に全成果物マージ済 (PR #11・#12 merged)" and
"main HEAD ≈ 21a253e 相当". Verified against the remote:

- `origin/main` = `eec5849` (the *legacy* IONE stratification codebase:
  `methods.py`, `run_simulation.py`, old README). It does **not** contain
  the aggregate-audit package.
- `git merge-base --is-ancestor 21a253e origin/main` → false.
- PR #12 is marked "closed (merged)" on GitHub, but `main` was
  subsequently reset/overwritten (sync force-push pattern noted in project
  memory). The JOSS package exists **only** on branch
  `devin/179179158-ione-naming` (= PR #12 head).

Action taken: the AJS work branches from `21a253e`, not from `main`.
The A4 PR will target `main`; reviewers should be aware the merge will
be effectively a rewrite of `main`'s content lineage (the legacy code
remains reachable via git history and `docs/legacy_ione.md`).

## 2. Inventory (at 21a253e)

| path | contents |
|---|---|
| `ione/__init__.py` (23) | package docstring, version 0.2.0, new expansion |
| `ione/aggregate.py` (132) | `ArmCount`, `SubgroupTable` (crude RR/RD/OR + Wald CIs, Haldane correction), `EffectSummary.check_consistency`, `sufficiency_report` |
| `ione/identifiability.py` (191) | LP engine (scipy linprog/HiGHS): sharp RD bounds; verdicts ROBUST_TREAT / ROBUST_NO_TREAT / REVERSIBLE / INFEASIBLE / UNSUPPORTED (+ legacy aliases SUFFICIENT/UNIDENTIFIABLE); `audit_decision` (prev1 or arm_weights, outcome_margin+mix, threshold); `borrow_check` (LOSO retrospective) |
| `ione/augmentation.py` (102) | cost-ordered `AugmentationOption` catalog; classes sufficient_assumed / potentially_informative / irrelevant / infeasible / unknown; no unconditional `resolves` |
| `ione/data.py` (57) | built-in RECOVERY, ISIS-2, REACT `EffectSummary`s with DOIs |
| `ione/cli.py` (126) | `ione audit` (--study/--csv/--target/--unmeasured-modifier/--threshold), `ione borrow-check`; JSON output incl. proximity profile |
| `ione/proximity.py` (20) | `ProximityProfile` (status, channels, margin⁻, top-z); descriptive only |
| `tests/test_aggregate_audit.py` (241) | 27 tests; LP vs closed-form algebra to 1e-8; enumeration cross-check; real-data reproduction; consistency/augmentation/CLI |
| `paper/paper.md` (102), `paper.bib` (50) | JOSS paper (568 words); bib: Manski 2003, RECOVERY, ISIS-2, REACT, legacy IONE |
| `docs/aggregate_audit/` | README (CSV spec, verdict table, failure modes), F0_F8_REPORTS.md, JOSS_GATE_AUDIT.md |
| `DECISION.md` | finishing-pass log, CONDITIONAL GO |
| `FINAL_NAMING_QC.md` | naming alignment QC record |
| `docs/legacy_ione.md` | original expansion preserved as history |
| `CITATION.cff`, `LICENSE` (MIT), `pyproject.toml` | dist `ione-audit` 0.2.0, `ione` CLI, numpy+scipy only |
| `.github/workflows/` | tests.yml (py3.9/3.11/3.12), draft-pdf.yml |
| legacy tree | `methods.py`, `run_simulation.py`, `data_generation.py`, `evaluation.py`, `visualization*.py`, `results/` — pre-aggregate-audit code, kept for history |

## 3. Implemented vs. not implemented

Implemented (verified by reading + running):
- Binary stratum x ∈ {0,1}, binary outcome, two arms; arm-level margins
  (p0bar, p1bar) → polytope feasible set; sharp conditional-RD bounds via
  two LPs; solver status + max residual reported.
- Verdicts as five disjoint states; INFEASIBLE (inconsistent margins),
  UNSUPPORTED (missing prevalence/mixing, solver failure) never conflated.
- Common-vs-arm-specific stratum prevalence; CLI auto-selects arm weights
  when |q1−q0| > max(2·SE, 0.01).
- Consistency check: subgroup sums vs overall; error vs warning split.
- Augmentation: cost-ordered, assumption-stated, never guarantees resolution.
- Borrow check: fixed-effect pooled log-RR of *other* subgroups vs actual;
  retrospective caveat enforced in output.
- Crude RR/RD/OR with Wald CIs; Haldane correction for zero cells.

Not implemented / out of scope (concept only, not claimed):
- No sampling uncertainty in bounds (bounds are identification bounds on
  point margins, not confidence intervals — must be stated in paper).
- No multi-valued/continuous strata or outcomes; no >2 arms.
- No adjusted estimands; no external validity; no prospective borrowing
  method; no minimum sample-size claims.
- "Proximity profile" is a descriptive tuple only — keep as minor feature.

## 4. Real-data audit (published aggregate counts)

| study | source | data used | verified |
|---|---|---|---|
| RECOVERY dexamethasone | NEJM 2021;384:693-704, DOI 10.1056/NEJMoa2021436 (PMC7383595) | overall 482/2104 vs 1110/4321 (28-d mortality); subgroups IMV 95/324 vs 283/683, O2 298/1279 vs 682/2604, noO2 89/501 vs 145/1034 | crude RR noO2 = 1.267 (harm) vs pooled-others 0.835 (benefit) → documented direction reversal; tests assert |RR−0.708|<0.005 IMV |
| ISIS-2 | Lancet 1988;2:349-360, DOI 10.1016/S0140-6736(88)92833-4 | aspirin arm overall 804/8587 vs 1016/8600; SK stratum 791/8592 vs 1029/8595; combo 343/4292 vs 568/4300 (5-wk vascular mortality) | tests assert RR 0.767, RD −0.0523 |
| WHO REACT | JAMA 2020;324(13):1330-1341, DOI 10.1001/jama.2020.17023 | pooled 222/678 vs 425/1025 (28-d mortality); SAE subgroup | published measure = fixed-effect OR 0.66; crude OR reproduced to <0.03 |

Cautions recorded: adjusted vs crude estimates not mixed (REACT's
published OR is model-based; tool reports crude); event definitions
(28-d mortality, 5-wk vascular mortality) kept per-study; subgroup
count provenance relies on prior PMC cross-verification — re-verified
against cited sources in Gate A3.

## 5. Environment & reproduction

- OS Ubuntu (Devin VM), Python 3.10.12, pip upgraded (PEP 621).
- `pip install -e ".[test]"` → OK; scipy 1.15.3, numpy 2.2.6.
- `pytest tests/ -q` → **27 passed** (log: `ajs/audit/logs/pytest_a0.txt`).
- CLI smoke: `ione audit --study recovery --target noO2` → REVERSIBLE,
  bounds [−1.000, +0.959], solver 0, residual ~3e-17.
- Note: handoff's example `ione audit --study recovery --target-x 1` is
  stale; correct flags are `--target noO2` (no `--target-x` exists).

## 6. Missing inputs (recorded, not blocking)

- `IONE_JOSS_NAMING_PACKAGE.zip` / `IONE_JOSS_FINISHING_PACKAGE.zip` were
  named as inputs but not attached to this session; the on-branch state
  at 21a253e is treated as the frozen input (it post-dates those zips).
- JOSS rejection letter text not attached; prompt states reasons were
  continuous-development/external-collaboration/track-record criteria —
  treated as such, not as statistical criticism.
- ORCID and official English affiliation name still unconfirmed
  (author action pending from prior gate; AJS manuscript will mark
  affiliation as "to be confirmed by author" unless resolved).
