PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip

export PYTHONPATH := src
export OMP_NUM_THREADS := 2
export OPENBLAS_NUM_THREADS := 2
export MKL_NUM_THREADS := 2
export NUMEXPR_NUM_THREADS := 2

.PHONY: install test reproduce clean-derived

install:
	$(PIP) install -r requirements-lock.txt

test:
	$(PYTHON) -m pytest

reproduce: test
	$(PYTHON) scripts/run_pipeline.py

clean-derived:
	rm -rf data/processed models outputs/figures outputs/hypergraphs outputs/reports outputs/tables run_manifest.json
	mkdir -p data/processed models outputs/figures outputs/hypergraphs outputs/reports outputs/tables outputs/logs
