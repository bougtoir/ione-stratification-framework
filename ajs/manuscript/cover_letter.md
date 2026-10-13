# Cover letter — Austrian Journal of Statistics

Dear Editors,

I am submitting "IONE: Identifiability-Oriented Navigation of Evidence
for Auditing Aggregate Clinical Trial Data" for consideration in the
Austrian Journal of Statistics.

When a randomized trial is statistically sound but a clinician's patient
belongs to a specific subgroup, the published arm-level margins and
subgroup tables are often all that is available. Whether those
aggregates can even support a subgroup-specific decision is a question
of identification, not estimation — and it is one that existing software
does not answer. Meta-analysis packages synthesize published effects;
sensitivity-analysis tools quantify robustness of identified estimates;
bound commands in econometrics require microdata or instrumental
variables. What a researcher holding only a printed report needs — is
the subgroup decision already fixed by the published numbers, could it
still reverse, and which additional *reportable* summary would narrow
the answer — has had no tested, documented tool.

The package `ione` closes that practical gap. It computes sharp bounds
on stratum-specific risk differences from published arm-level margins
by linear programming, reports five strictly separated verdicts (so that
inconsistent tables, missing specification, and genuine
nonidentification are never conflated), and — the feature I believe your
readers will find most useful — orders the *additional aggregate
summaries the original investigators could still report* by burden,
starting with a near-zero-cost cross-tabulation request, while honestly
declining to promise that any augmentation resolves the decision. Every
stratum audit is organized as an explicit information ladder — arm-level
totals (L1), plus stratum denominators (L2), plus arm-by-stratum event
counts (L3) — so the paper shows exactly which published table changes
the answer, and marks lower levels as deliberate ablations when the full
table was in fact published. The applications demonstrate both
directions on source-verified data: RECOVERY (dexamethasone) publishes
all three levels, so the crude stratum risk differences are
point-identified — including the unfavourable direction in the no-oxygen
subgroup — while ISIS-2 (aspirin/streptokinase) published its
time-from-onset subgroups only as odds reductions, leaving the audit at
L1 and making the missing table concrete. A documented counterexample
from the WHO REACT meta-analysis shows why post-treatment variables must
never define a stratum, and a retrospective borrow check on RECOVERY
reproduces a real direction reversal that unexamined pooling would have
produced.

The statistical content is deliberately classical — partial
identification via marginal-consistency linear programs, in the lineage
of Manski, Cross and Manski, King, and Balke and Pearl — and the paper
says so. What I claim is a reproducible audit workflow and verified
applications, in the applied/computational spirit that AJS publishes.
All results are reproducible: the data are published counts embedded in
the package, the bounds are verified against closed-form algebra and
enumeration, and the source code and tests are openly available at
https://github.com/bougtoir/ione-stratification-framework .

Disclosure: an earlier software description of this package was
submitted to the Journal of Open Source Software, which declined it on
scope/community criteria (not on the statistics); this manuscript is a
different, substantially expanded applied-statistics article and is not
under consideration elsewhere.

Suggested reviewers (optional, per guidelines): I would be happy to
propose names on request.

Sincerely,
Tatsuki Onishi
Shiga University, Data Science AI Innovation Research Promotion Center
