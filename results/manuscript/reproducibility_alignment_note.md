# Reproducibility alignment note — IONE revised submission

## Objective

All numbers, tables and figures in the revised manuscript must be reproducible from the public repository code with no hard-coded estimates.

## Pipeline

```
data_generation.py  ->  run_simulation.py / real_data_analysis.py  ->  results/*.csv
                                                              |
                                                              v
                                                   generate_summary.py
                                                              |
                                                              v
                                                   generate_manuscript.py
                                                              |
                              results/manuscript/IONE_revised_manuscript.docx
                              results/figures/*.png
                              results/figures/pptx/figures.pptx
```

## Reproduction commands

From a clean clone with Python 3.10+:

```bash
pip install -r requirements.txt
python3 run_simulation.py                  # produces results/phase1_results.csv, sensitivity_results.csv, nonlinearity_results.csv
python3 real_data_analysis.py              # produces results/real_data/real_data_results.csv
python3 generate_summary.py                # produces results/summary/*.csv
python3 generate_manuscript.py             # produces results/manuscript/IONE_revised_manuscript.docx and results/figures
```

## Data sources

- **Simulation:** no external data; DGM parameters are in `data_generation.py`.
- **Semi-synthetic illustrations:** aggregate counts from five published Simpson's-paradox examples. Sources are cited in the manuscript and the reconstruction code is in `real_data_analysis.py`.

## Hard-code audit

- `generate_manuscript.py` reads all numbers from `results/summary/*.csv`.
- The only literal strings in the manuscript generator are section names, journal-specific formatting, and the reference list.
- No simulation estimates are typed into the manuscript.

## Verification

A clean clone of the public repository was used to regenerate the summary tables and manuscript from the committed results CSVs. The regenerated Word document has identical paragraph text to the version in the working repository. To verify from scratch, run the full pipeline and compare the regenerated `results/manuscript/IONE_revised_manuscript.docx` with the submitted version. The text and table values should match exactly up to floating-point rounding.
