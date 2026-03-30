[Date]

[Corresponding author name]
[Affiliation]
[Address]
[Email]

---

**To:** The Editors, BMC Medical Research Methodology
**Collection:** Causal inference and observational data vol. 2

**Re:** Submission of original research article — "IONE: Incoherence-Oriented Neutralisation and Extraction for Detecting Hidden Population Structure in Observational Studies"

---

Dear Editors,

We are pleased to submit our manuscript entitled "IONE: Incoherence-Oriented Neutralisation and Extraction for Detecting Hidden Population Structure in Observational Studies" for consideration as an original research article in BMC Medical Research Methodology, specifically for the Collection "Causal inference and observational data vol. 2".

Observational studies remain susceptible to biases arising from hidden population structure — a single root cause that manifests as confounding, Simpson's paradox, undetected effect modification, the ecological fallacy, and non-collapsibility. Existing adjustment methods such as propensity scores and prognostic scores address only measured confounders and offer no mechanism for detecting subgroup structure driven by unmeasured variables. We sought to address this methodological gap by developing a framework that can both quantify population incoherence and extract coherent subpopulations using routinely measured variables alone.

In this manuscript, we present the IONE (Incoherence-Oriented Neutralisation and Extraction) framework, which operates in two stages: (1) detection of population incoherence using a coherence indicator (C1) derived from the I² heterogeneity statistic, and (2) extraction of coherent subpopulations through stratification based on multivariate patterns in measured variables. We evaluated six stratification methods in two families — decision power-based methods exploiting the outcome and feature score-based methods operating in the covariate space alone — through a comprehensive Monte Carlo simulation study following the ADEMP framework (66,600 evaluations across 9,300 scenarios) and empirical validation on five published instances of Simpson's paradox (kidney stone treatments, UC Berkeley admissions, COVID-19 case fatality rates, Israeli vaccine effectiveness, and the smoking–mortality paradox). Our key findings are: (i) the C1 coherence indicator reliably detected population incoherence in all simulated and empirical settings; (ii) for discrete two-group structures with strong unmeasured variable influence, stratification achieved high accuracy (Adjusted Rand Index > 0.7); and (iii) decision power-based methods consistently outperformed feature score-based methods, establishing a clear methodological hierarchy.

We believe this manuscript is well suited to BMC Medical Research Methodology and to this Collection for several reasons. First, the work directly addresses the Collection's core themes of bias mitigation techniques and confounding control in observational data, proposing a novel approach that complements existing propensity score and prognostic score methods. Second, the combination of a rigorous simulation study reported under the ADEMP framework with empirical validation on well-known datasets demonstrates both theoretical grounding and practical relevance — a combination that the Collection specifically encourages. Third, the proposed C1 coherence indicator offers a practical reporting tool that could be incorporated into standard observational study practice, aligning with the Collection's interest in transparency tools for causal inference studies. The interdisciplinary approach — bridging meta-analytic heterogeneity statistics, machine learning, and clinical epidemiology — reflects the Collection's encouragement of solutions spanning statistics, computer science, and biomedical sciences.

We confirm that this manuscript has not been published elsewhere and is not under consideration by another journal. All authors have read and approved the manuscript and agree with its submission to BMC Medical Research Methodology. The authors declare no competing interests. No ethical approval was required as this study uses simulated data and previously published aggregate data only.

The simulation code and all analysis scripts are available in a public repository to ensure full reproducibility.

We thank you for considering our manuscript and look forward to your response.

Yours sincerely,

[Corresponding author name]
on behalf of all authors
