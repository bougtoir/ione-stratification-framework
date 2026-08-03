# Next-journal proposal for IONE after BMC MRM rejection

## State of the manuscript

- **Current status:** **Final rejection from BMC Medical Research Methodology after a revise-and-resubmit (3/30 submission → 6/3 revision requested → 8/3 reject).** The editor explicitly stated that the identified concerns are not viewed as addressable through further revision at BMC MRM, so a simple resubmission is not viable.
- **Core reviewer message:** The diagnostic idea (C1) is interesting, but the extraction claims are overstated, the metrics (especially C1 and W) need empirical grounding, and the oracle/ground-truth definitions remain unclear.
- **Required action before resubmission:** A **major reframing**, not just a point-by-point response. The paper should be repositioned as an **exploratory diagnostic sensitivity study** rather than a mature two-tier workflow. Concrete fixes include: reconciling the bias-reduction formula, resolving the W-oracle problem, recalibrating C1, redefining the ground truth, and adding a code archive.

---

## Recommended next targets (in order)

### 1. Statistics in Medicine (primary recommendation)

| Item | Detail |
|------|--------|
| Publisher | Wiley |
| Scope | Biostatistics and epidemiological methods; simulation studies and method comparison are central to the journal. |
| IF | ~1.6–2.0 (2024) |
| Peer review | Yes |
| OA | Hybrid |
| APC | **$0 if you choose subscription publication**; ~$4,200 USD if OA |
| Fit | **Strong.** The revised manuscript is a simulation-based method-development study with active comparators, sensitivity analyses, and empirical illustrations—exactly the content Stat Med publishes. The ADEMP structure, MC SE reporting, and systematic variation of Z→X influence all align with Stat Med expectations. |

**Framing for Stat Med**
- Title idea: *"A coherence diagnostic for hidden population structure in observational studies: a simulation study of stratification-based extraction"*
- Lead with **C1 as an exploratory diagnostic**; present extraction as a secondary, conditionally successful proof-of-concept.
- Emphasise the ADEMP-compliant simulation design and the systematic variation of Z→X influence.
- Keep the semi-synthetic examples but clearly label them as **illustrations**, not validation.
- **Do not claim** that C1 or W are ready for clinical use; instead, frame them as sensitivity diagnostics that need further calibration.

**Why first:** It is the most natural peer-reviewed venue for the current evidence base, has no APC under subscription publication, and is less risky than higher-IF epidemiology journals for a simulation-only proof-of-concept.

---

### 2. Statistical Methods in Medical Research (SAGE)

| Item | Detail |
|------|--------|
| Publisher | SAGE |
| Scope | Statistical methodology in medical research. |
| IF | ~1.5–2.0 (2024) |
| Peer review | Yes |
| OA | Hybrid |
| APC | $0 if subscription; ~$3,900 USD if OA |
| Fit | Strong. Publishes simulation studies and methodological development. |

**Framing:** Similar to Stat Med, but with more focus on the formal definition of the coherence metric and the method comparison.

**Why second:** Good fallback if Stat Med desk-rejects or reviewers ask for even stronger theory.

---

### 3. Epidemiology (Lippincott Williams & Wilkins)

| Item | Detail |
|------|--------|
| Publisher | LWW |
| Scope | Epidemiologic methods; short methods papers are welcome. |
| IF | ~4.4–4.7 |
| Peer review | Yes |
| OA | Subscription-only (no OA option, **$0**) |
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

- **American Journal of Epidemiology / International Journal of Epidemiology:** IF ~4.8–6.4. Simulation-only papers are harder to place here. A real individual-level clinical data application (e.g. MIMIC-IV, UK Biobank, or a large claims database) would substantially strengthen the case.
- **Biometrics:** IF ~1.5–2.0. Would require formal theoretical guarantees (consistency, asymptotic behaviour of C1) beyond the current simulation design.

---

## Proposed decision

1. **Primary target:** *Statistics in Medicine* after the major revision.
2. **Backup target:** *Statistical Methods in Medical Research*.
3. **Consider Epidemiology** only if the revision can be condensed into a tight 3,500-word methods paper with C1 as the single main message.

The revision should be completed before any submission, because the same reviewer concerns will be raised at these journals.

---

## ONISHI framework coordination

The final goal is to publish **LINKO**, **IONE**, **KOTHA** as component papers and then a unifying **ONISHI** paper. Given the BMC MRM rejections of IONE and KOTHA, the current best allocation is:

| Paper | Suggested next target | Rationale | APC (subscription) |
|-------|----------------------|-----------|-------------------|
| **LINKO** | **BMC MRM regular issue** or **Research Synthesis Methods** | Meta-analysis methodology; BMC MRM regular is lower risk, but if already rejected, use RSM / *Systematic Reviews*. | $3,090 if BMC MRM; $0 if RSM |
| **IONE** | **Statistics in Medicine** | Observational/simulation methods; strong fit after reframing. | $0 |
| **KOTHA** | **Research Synthesis Methods** | Meta-analysis/RCT integration; already prepared for RSM and is the first choice in the KOTHA session. | $0 |
| **ONISHI** | **Research Synthesis Methods** or **AJE** | Unifying framework; RSM package is already prepared, but AJE is faster and has higher IF. | $0 |

**Practical sequencing for citations:**
1. Put all three component papers on **medRxiv/arXiv** with versioned DOIs immediately.
2. Submit IONE to Stat Med and KOTHA to RSM first (they are ready after their respective revisions).
3. LinkO should be submitted only after deciding whether to stay with BMC MRM or move to RSM.
4. Submit ONISHI only after at least the preprints of the three components are public, so ONISHI can cite them as companion papers.

**Risk note:** BMC MRM has now rejected both IONE and KOTHA after peer review. If LINKO is also rejected by BMC MRM, the fallback is **Research Synthesis Methods** for LINKO (if methodological innovation can be sharpened) or **Systematic Reviews** (BMC series, full OA).
