# Next-journal proposal for IONE after BMC rejection

## State of the manuscript

- **Current status:** Hard reject from BMC Medical Research Methodology after peer review.
- **Core reviewer message:** The diagnostic idea (C1) is interesting, but the extraction claims are overstated, the metrics need calibration/grounding, and the oracle/ground-truth definitions are unclear.
- **Required action before resubmission:** A major revision that narrows the contribution to an exploratory diagnostic framework, fixes metric inconsistencies, and adds calibration/implementation detail.

---

## Recommended next targets (in order)

### 1. Statistics in Medicine (primary recommendation)

| Item | Detail |
|------|--------|
| Publisher | Wiley |
| Scope | Biostatistics and epidemiological methods; simulation studies and method comparison are central to the journal. |
| IF | ~1.6–2.0 |
| Peer review | Yes |
| OA | Hybrid |
| APC | ~$3,900 USD if OA |
| Fit | **Strong.** The manuscript is a simulation-based method-development study with active comparators, sensitivity analyses, and empirical illustrations—exactly the content Stat Med publishes. |

**Framing for Stat Med**
- Title idea: *"A coherence diagnostic for hidden population structure in observational studies: a simulation study of stratification-based extraction"*
- Lead with C1 as an exploratory diagnostic; present extraction as a secondary, conditionally successful proof-of-concept.
- Emphasise the ADEMP-compliant simulation design and the systematic variation of Z→X influence.
- Keep the semi-synthetic examples but clearly label them as illustrations, not validation.

**Why first:** It is the most natural peer-reviewed venue for the current evidence base and has lower risk than higher-IF epidemiology journals.

---

### 2. Statistical Methods in Medical Research (SAGE)

| Item | Detail |
|------|--------|
| Publisher | SAGE |
| Scope | Statistical methodology in medical research. |
| IF | ~1.5–2.0 |
| Peer review | Yes |
| OA | Hybrid |
| Fit | Strong. Publishes simulation studies and methodological development. |

**Framing:** Similar to Stat Med, but with more focus on the formal definition of the coherence metric and the method comparison.

**Why second:** Good fallback if Stat Med desk-rejects or reviewers ask for even stronger theory.

---

### 3. Epidemiology (Lippincott Williams & Wilkins)

| Item | Detail |
|------|--------|
| Publisher | LWW |
| Scope | Epidemiologic methods; short methods papers are welcome. |
| IF | ~4.7–5.0 |
| Peer review | Yes |
| OA | Hybrid |
| Fit | Moderate. The journal values concise, high-impact methods papers. The current manuscript is too long and too exploratory as written, but a sharply shortened version focused on C1 could fit the "Methods" section. |

**Framing:**
- Title idea: *"C1: an I²-based diagnostic for hidden subgroup structure in observational studies"*
- Reduce to ~3,500 words; one main figure (C1 calibration), one table (simulation summary), one empirical illustration.
- De-emphasise extraction; position IONE as a pre-analysis diagnostic.

**Why third:** Higher IF and visibility, but the paper would need substantial shortening and a stronger single message.

---

### 4. Journal of Causal Inference (De Gruyter)

| Item | Detail |
|------|--------|
| Publisher | De Gruyter |
| Scope | Causal inference methodology across disciplines. |
| IF | ~1.0–1.5 (lower visibility) |
| Peer review | Yes |
| OA | Hybrid |
| Fit | Good if the paper is framed around causal assumptions, unmeasured confounding, and the diagnostic role of coherence. Less suitable for purely empirical simulation illustration. |

**Framing:** Focus on the causal motivation (unmeasured confounding, effect modification, non-collapsibility) and the distinction from propensity-score and proximal-causal-inference approaches.

**Why fourth:** Good scope match but lower IF; consider only if the first three are unsuccessful.

---

## Higher-tier options (only if major additions are made)

- **American Journal of Epidemiology / International Journal of Epidemiology:** IF ~5–6. Simulation-only papers are harder to place here. A real individual-level clinical data application (e.g., MIMIC-IV, UK Biobank, or a large claims database) would be needed.
- **Biometrics:** IF ~1.5–2.0. Would require formal theoretical guarantees (consistency, asymptotic behaviour of C1) beyond the current simulation design.

---

## Proposed decision

1. **Primary target:** *Statistics in Medicine* after the major revision.
2. **Backup target:** *Statistical Methods in Medical Research*.
3. **Consider Epidemiology** only if the revision can be condensed into a tight 3,500-word methods paper with C1 as the single main message.

The revision should be completed before any submission, because the same reviewer concerns will be raised at these journals.
