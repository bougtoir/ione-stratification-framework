# Next-journal candidates after SMMR rejection

Decision date: 2026-08-18
Manuscript: IONE (Incoherence-Oriented Neutralisation and Extraction) stratification framework
Previous submission: *Statistical Methods in Medical Research* (SMMR), manuscript #SMM-26-0746 — desk-rejected without stated reason.
Chosen next journal: **Computational Statistics & Data Analysis (CSDA)**
Repository: `bougtoir/ione-stratification-framework`, branch `devin/ione-smmr-v1`, commit `b75f8e4`.

## Candidate comparison (APC prioritized)

Sorted by hybrid-OA APC from low to high. All journals also offer a subscription (no-APC) route unless otherwise noted.

| Priority by APC | Journal | Publisher | APC (hybrid OA, USD) | Non-OA option | 2024 IF (approx.) | Scope match |
|---|---|---|---|---|---|---|
| 1 (chosen) | *Computational Statistics & Data Analysis* | Elsevier | ~$3,360 | Subscription OK | ~1.6–1.8 | Strong — computational/methodological statistics, simulation benchmarking |
| 2 | *Journal of the Royal Statistical Society Series C (Applied Statistics)* | Oxford University Press (RSS) | ~$3,300 (GBP £2,621 / EUR €3,150) | Subscription OK | ~1.3–1.4 | Moderate — applied statistics with real-world application; pure simulation is less central |
| 3 | *Biometrics* | Oxford University Press (International Biometric Society) | ~$3,710 | Subscription OK | ~1.4–1.8 | Moderate — biostatistical methods; previous publisher was Wiley until 2024 |
| 4 | *Pharmaceutical Statistics* | Wiley (PSI official journal) | ~$3,400 (Scimago estimate; exact APC to be confirmed) | Subscription OK | ~1.3 | Weak-to-moderate — industry/pharmaceutical applications, not simulation-only |
| 5 | *Biometrical Journal* | Wiley | ~$4,120 | Subscription OK | ~1.8–2.1 | Moderate — biostatistics/life sciences, reproducible research required |
| 6 | *Statistics in Medicine* | Wiley | ~$4,940–$5,190 | Subscription OK | ~1.8–2.0 | Moderate — medical statistics, but prior reviewer risk seen |

Excluded: *Statistical Methods in Medical Research* (already rejected).

## Selection rationale: CSDA

- **APC**: lowest confirmed fee among confirmed candidates ($3,360).
- **Scope**: official journal of CMStatistics and IASC; explicitly welcomes computational statistics and methodological development, including simulation studies.
- **Non-OA route**: available if no OA mandate.
- **Risk**: less clinically-oriented than SMMR, so the title/abstract should emphasize the statistical/computational contribution and de-emphasize clinical interpretation.

## Notes for CSDA adaptation

- Follow CSDA *Guide for Authors* exactly (Elsevier): https://www.sciencedirect.com/journal/computational-statistics-and-data-analysis/publish/guide-for-authors
- CSDA manuscript style is typically LaTeX or Word; verify equation format policy.
- Figures/tables: Elsevier requires separate files for figures and embedded citations; check resolution/format requirements.
- Abstract length and keyword requirement must be checked before rewriting.
- References: Elsevier style (Vancouver/numbered, journal-dependent); confirm exact citation format.
- Title does not need to be changed unless CSDA word limits or scope demand it; current title already includes IONE and the benchmark framing.
- The supplementary material pipeline (`generate_summary.py` → `generate_rsm_tables.py` → `generate_ione_rsm_v3.py`) should regenerate all numbers/figures before submission.

## Data sources consulted (2026-08-18)

- CSDA APC: ScienceDirect journal page, https://www.sciencedirect.com/journal/computational-statistics-and-data-analysis (APC USD 3,360).
- JRSS C notes for authors 2025: https://rss.org.uk/RSS/media/File-library/Publications/RSS-journal-notes-for-authors-2025.pdf (OnlineOpen fee £2,621 / $3,300 / €3,150).
- Biometrics APC: OpenAlex / JournalsHub (~$3,710).
- Biometrical Journal APC: Wiley hybrid APC list (~$4,120).
- Statistics in Medicine APC: JournalsHub / Wiley hybrid list (~$4,940).
- Pharmaceutical Statistics APC: Scimago estimated APC (~$3,351) — exact publisher page not located.
- Impact factors: SciJournal, JournalMetrics.org, Wiley journal pages, Scimago, Resurchify, Exaly; figures are rounded 2-year IF values for 2024.

## Open questions before CSDA submission

1. Confirm CSDA exact abstract word limit and structured/unstructured requirement.
2. Confirm CSDA reference style and figure/table submission format.
3. Decide whether to publish OA or subscription.
4. Update cover letter to target CSDA scope (computational/methodological).
