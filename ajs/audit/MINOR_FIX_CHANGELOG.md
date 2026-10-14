# Minor-fix changelog (adversarial-review response)

Branch: `devin/1791942979-ione-ajs-minorfix`, base `main` @ b0e62d7 (PR
#15 merged). No numeric results, figures, data, or analysis code
changed. Tests: `python3 -m pytest tests/ -q` → 34/34 passed
(Python 3.11.9, this VM). PDF: latexmk rebuild, 10 pp, 0 LaTeX warnings
in `ione_ajs.log`.

| ID | Change | File / location | Verification |
|----|--------|-----------------|--------------|
| I-01 | Added paragraph after verdict itemize: five *primary* states; `SUFFICIENT`/`UNIDENTIFIABLE` are legacy enum aliases kept for API compatibility, never emitted by audit outputs | `ione_ajs.tex`, §Verdicts (after itemize) | matches `ione/identifiability.py` enum (7 members incl. 2 legacy) |
| I-02 | Contribution (iii): "three source-verified applications to landmark trials and a meta-analysis" → "two source-verified applications to landmark trials plus one deliberately excluded counterexample" | `ione_ajs.tex` Intro | consistent with §Results (RECOVERY+ISIS-2 applications, REACT counterexample) |
| I-03 | Added clause: at L2 the prevalences come from the published denominators and are conditioned on as given, not treated as exact population quantities | `ione_ajs.tex` Methods, "Three conditions govern interpretation", second condition | consistent with limitations paragraph |
| I-04 | Added parenthetical: all demonstrations use τ=0; other thresholds require explicit user-specified analysis, not separately validated | `ione_ajs.tex` §Results, Table 2 lead-in | matches `reproduce_r.py` (threshold=0) |
| I-05 | "Python 3.9–3.12" → "Python 3.9, 3.11, and 3.12" | `ione_ajs.tex` §Implementation | matches CI matrix {3.9, 3.11, 3.12} |
| I-06 | New `ajs/analysis/README.md`: `r_*` artifacts authoritative; `reproduce_a3.py`, `a3_*.csv`, `fig_bounds_vs_q.pdf`, `fig_verdicts.pdf` labelled superseded historical evidence (kept, not deleted) | `ajs/analysis/README.md` (new) | file list cross-checked vs `ajs/audit/` + `ajs/figures/` |
| I-07 | README documents legacy CLI JSON key `"sufficiency"`; in-code comment added above the `print` | `ajs/analysis/README.md`, `ione/cli.py` | key name unchanged — no API break |
| I-08 | Verified, not fabricated: PR #13/#14/#15 are merged; `main` @ b0e62d7 contains the full `ione/` package, `ajs/` tree, tests | repo inspection | `git log origin/main`; manuscript repo URL unchanged |
| I-09 | Author metadata rechecked: affiliation "Shiga University, Data Science and AI Innovation Research Promotion Center / 1-1-1 Banba, Hikone, Shiga 522-8522" and ORCID remain author-reported, not independently confirmed | `ione_ajs.tex` title block | flagged as submission-time author confirmation (genuine unresolved item) |
| I-10 | Added limitation clause: demonstrations drawn from cardiovascular and respiratory trials; workflow domain-agnostic but value across other specialties untested | `ione_ajs.tex` §Limitations | one clause, no new datasets demanded |

Also synchronized: Intro roadmap "reports the three real-data audits" →
"reports the real-data audits" (same I-02 consistency).

New issues found: none fatal, none submission-blocking. The
"and a meta-analysis" phrase removed under I-02 was itself a residual
misdescription (all three datasets are trials) — fixed as part of the
same edit.
