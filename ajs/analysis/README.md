# Reproduction instructions and artifact status

Authoritative reproduction entry point (information-level results, the
version reported in the manuscript):

    python3 reproduce_r.py        # writes r_levels.csv, r_ledger.csv,
                                  # fig_levels.pdf, r_qc.txt into ajs/audit/

Superseded historical evidence (kept, not deleted): `reproduce_a3.py`
and its outputs `a3_bounds_vs_q.csv`, `a3_constructed.csv`,
`a3_math_tests.csv`, plus the older figures `fig_bounds_vs_q.pdf` and
`fig_verdicts.pdf` under `ajs/audit/` and `ajs/figures/`. These belong to
the pre-information-level revision; where their results differ from the
`r_*` artifacts, the `r_*` files are authoritative.

CLI output note: the JSON emitted by `ione audit` uses the top-level key
`"sufficiency"`, a legacy field name from the original IONE vocabulary.
It is retained for API compatibility; the canonical verdict values it
contains are the five primary states described in the manuscript.
