# Gate A1 — Citation ecology audit

Rule applied: every citation must back a specific claim in the text;
no decorative or prestige citations. Planned mapping (final placement
audited again in Gate A4):

| citation | claim it supports | where |
|---|---|---|
| Manski 2003 | partial identification = bounds from incomplete info; lineage of the method | Intro, Methods |
| Cross & Manski 2002 | marginals-only aggregation → interval-valued conditional quantities | Intro, Methods |
| King 1997 | deterministic bounds from aggregate 2×2 margins (ecological inference) — direct ancestor of our construction | Methods |
| Balke & Pearl 1997 | LP formulation for sharp treatment-effect bounds | Methods |
| Horowitz & Manski 2000 | bounds under missing covariate/outcome data in RCTs | Intro |
| Pearl & Bareinboim 2014 | external validity/transport needs assumptions — motivates auditing what aggregates alone identify | Intro, Discussion |
| VanderWeele & Ding 2017 | sensitivity-analysis answers a different question (bias robustness) | Intro (tool-gap), Discussion |
| Viechtbauer 2010 (metafor) | existing software synthesizes effects but doesn't audit identifiability | Intro (tool-gap) |
| tebounds (Stata J 2015), bpbounds (2011) | bounds software exists for IV/endogeneity but requires microdata or different designs | Intro/Discussion comparison table |
| Moon 2026 (Econometric Reviews) | independent concurrent development of the same marginal-consistency program — situates novelty honestly (workflow, verdict taxonomy, augmentation ordering, not the math) | Methods/Discussion |
| Imbens & Manski 2004 | our bounds are identification bounds, not CIs; sampling uncertainty is a separate unsolved layer | Methods limitations, Discussion |
| RECOVERY 2021, ISIS-2 1988, REACT 2020 | provenance of the three worked datasets | Results |
| legacy IONE (repo docs) | historical naming note only | Footnote/intro note |
| Python/NumPy/SciPy/HiGHS | software used — AJS requires citing software | Methods/implementation |

Exclusions deliberately NOT cited (checked, not needed to support a claim):
generic borrowing methods (robust MAP, power prior) — mentioned in text
as categories via one representative cite if kept; JOSS-style software
citations irrelevant to AJS readers.

Software-gap claim wording (verified, not overstated): "no released tool
we verified computes sharp conditional-RD bounds from published arm-level
margins AND classifies the result into decision verdicts with
cost-ordered reportable augmentations." Verified feature lists:
metafor (synthesis), EValue/tipr (bias sensitivity), tebounds/bpbounds
(IV bounds, microdata), rbounds (nonparametric Manski ATE bounds on
microdata). Moon 2026 provides the same program for a different
estimand family in economics — cited as concurrent work, so the
novelty claim is framed as workflow + clinical-trial application, not
first-ever derivation.
