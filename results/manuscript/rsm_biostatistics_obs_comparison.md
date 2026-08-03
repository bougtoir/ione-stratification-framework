# IONE: Research Synthesis Methods vs Biostatistics vs Observational Studies — scope-fit comparison

| Dimension | Research Synthesis Methods (RSM) | Biostatistics | Observational Studies |
|---|---|---|---|
| **Publisher / access** | Cambridge University Press (from 2025; fully OA) | Oxford University Press (hybrid OA) | University of Pennsylvania Press (Diamond OA) |
| **Latest IF (approx.)** | 6.1–8.0 | 2.0–2.1 | ~1.1 |
| **APC** | $2,740 / £1,960 | ~$3,100–$3,500 (hybrid; verify) | Free (no APC) |
| **Scope in one sentence** | Methods for designing, conducting, analyzing and reporting **systematic research synthesis** (systematic reviews, meta-analysis, evidence synthesis). | Innovative statistical methods motivated by and applied to **human health/disease** problems. | All aspects of **observational studies**: protocols, methodologies, data sets, software, and analyses. |
| **Scope fit for IONE** | **Fair / weak** | **Strong** | **Excellent** |
| **Natural article type** | Methodological research / empirical simulation | Original Research Article | Original Research Paper or Methods Tutorial |
| **Key practical requirement** | ORCID, Overleaf/ScholarOne, author-date references. | Manuscript Central, Word or LaTeX, **public code repository + archived code**, 25 pages in draft mode. | Scholastica, **LaTeX required at acceptance**, author-year (natbib) references. |

## 1. Research Synthesis Methods (Cambridge University Press)

**Scope fit**
- RSM is explicitly about *research synthesis* — systematic reviews, meta-analyses, and evidence-synthesis methodology.
- IONE is a single-study diagnostic for hidden population structure (confounding / effect modification) in observational data. It does **not** synthesize multiple studies.
- A plausible reframing would be to pitch C1/W as heterogeneity diagnostics for **meta-analytic strata** or for individual participant data (IPD) meta-analysis. RSM’s scope includes “synthesis of individual participant data” and “issues of study quality, reporting or other systematic biases.”
- However, the current manuscript’s examples (Simpson paradox, semi-synthetic data) are not framed as synthesis problems, so the fit is **not natural** without substantial rewriting.

**Practical considerations**
- Highest IF of the three and fully OA at a moderate APC.
- Submission via ScholarOne; ORCID required for corresponding author.
- Cambridge uses an author-date reference style (CambridgeA/CambridgeB); the current Vancouver-numbered reference list would need conversion.
- No strict word/page limit found, but methods papers are expected to be concise.

**Verdict**: High visibility, but only if you are willing to reframe IONE as a tool for research-synthesis heterogeneity (e.g., IPD meta-analysis or stratified evidence synthesis). Otherwise desk-reject risk is non-trivial.

## 2. Biostatistics (Oxford University Press)

**Scope fit**
- Biostatistics publishes “papers that develop innovative statistical methods with applications to the understanding of human health and disease.”
- IONE’s two-stage diagnostic (C1 + W), simulation benchmarking, risk-difference ATE estimand, and real-data illustrations map directly to this scope.
- The journal explicitly values: (1) methods motivated by substantive health/biomedical problems, (2) simulation studies, (3) reproducibility (code/data availability).
- The current manuscript’s Simpson-paradox examples and public code repository satisfy the “substantive problem + reproducibility” expectation.

**Practical considerations**
- Submission via Manuscript Central; Word acceptable for initial submission.
- 25-page limit in draft mode (not including refs/appendices).
- Strongly encourages/expects a public code repository and archived code (GitHub + Figshare/Zenodo).
- Reference style is journal-specific (CSL available); current Vancouver format may need adjustment.

**Verdict**: **Strong fit** with the current framing. If the primary claim is “a new biostatistical diagnostic for observational studies,” Biostatistics is a very natural target.

## 3. Observational Studies (University of Pennsylvania Press)

**Scope fit**
- The journal’s entire mission is observational studies, and it explicitly welcomes “methodologies for observational studies,” “software for observational studies,” and “analyses of observational studies.”
- IONE’s focus on hidden confounding/effect modification and stratification-based extraction in observational data is exactly the kind of methodology this journal exists to publish.
- “Original Research Paper” type fits: new statistical methods for observational data, with real-data illustration. “Methods Tutorial” also fits if the emphasis is pedagogical.

**Practical considerations**
- Diamond OA: free to read and free to publish (no APC).
- Submission via Scholastica; LaTeX template/style file required, and a LaTeX source file must be supplied after acceptance.
- Author-year references via natbib (`\citep{}`, `\citet{}`); the current Vancouver numbering must be converted.
- Original research papers are typically ≤ 25 pages excluding references/appendices.
- Newer journal with lower IF, but the audience is precisely observational-methods specialists.

**Verdict**: **Excellent scope fit**, easiest on cost, but requires LaTeX conversion and has lower impact factor/visibility.

## Comparative summary

| Criterion | Best fit |
|---|---|
| Scope match | **Observational Studies** |
| Prestige / IF | **Research Synthesis Methods** |
| Cost | **Observational Studies** (free) |
| Ease of formatting from current docx | **Biostatistics** (Word accepted) |
| Reproducibility expectation | **Biostatistics** and **Observational Studies** both strong |
| Need for reframing | **Research Synthesis Methods** (most reframing needed) |

## Recommendation

- If the manuscript can be kept close to its current form: **Biostatistics** is the strongest of the three — excellent scope fit, accepts Word, and has the reproducibility infrastructure already in place.
- If you are willing to convert to LaTeX and prioritize a perfect scope match over impact factor: **Observational Studies** is ideal and costs nothing.
- **Research Synthesis Methods** is attractive because of its high IF and full OA, but only if you can credibly reframe IONE as a method for research synthesis / meta-analytic heterogeneity; otherwise the risk of a scope-based rejection is high.
