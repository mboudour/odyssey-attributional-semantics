PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip

export PYTHONPATH := src
export PYTHONHASHSEED := 0
export OMP_NUM_THREADS := 2
export OPENBLAS_NUM_THREADS := 2
export MKL_NUM_THREADS := 2
export NUMEXPR_NUM_THREADS := 2

.PHONY: install test reproduce preview-visualizations visualize validate validate-visualizations clean-derived

install:
	$(PIP) install -r requirements-lock.txt

test:
	$(PYTHON) -m pytest

reproduce: test
	$(PYTHON) scripts/run_pipeline.py
	$(PYTHON) scripts/generate_hypergraph_visualizations.py
	$(PYTHON) scripts/validate_release.py
	$(PYTHON) scripts/validate_visualizations.py

preview-visualizations:
	$(PYTHON) scripts/generate_hypergraph_visualizations.py --mode preview

visualize:
	$(PYTHON) scripts/generate_hypergraph_visualizations.py --mode full
	$(PYTHON) scripts/validate_visualizations.py

validate:
	$(PYTHON) scripts/validate_release.py
	$(PYTHON) scripts/validate_visualizations.py

validate-visualizations:
	$(PYTHON) scripts/validate_visualizations.py

clean-derived:
	rm -rf data/processed models outputs/figures outputs/hypergraphs outputs/hypergraph_visualizations outputs/hypergraph_visualization_preview outputs/reports outputs/tables run_manifest.json
	mkdir -p data/processed models outputs/figures outputs/hypergraphs outputs/hypergraph_visualizations outputs/reports outputs/tables outputs/logs
