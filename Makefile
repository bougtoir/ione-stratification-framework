# Reproducible figures and numbers for the IONE stratification framework.
# The default target only regenerates summary CSVs and figure files.
# Use `make submission` to also build the JCMDS Word/PDF/zip submission package.

PYTHON ?= python3

.PHONY: all figures submission clean

all: figures

figures:
	$(PYTHON) generate_summary.py
	$(PYTHON) generate_ione_rsm_v3.py --figures-only

submission:
	$(PYTHON) generate_summary.py
	$(PYTHON) generate_rsm_tables.py
	$(PYTHON) generate_ione_rsm_v3.py

clean:
	rm -f results/summary/*.csv
	rm -f results/figures/*.png results/figures/*.eps
	rm -f results/figures/pptx/*.pptx
	rm -f results/commit_hash.txt
