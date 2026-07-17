PYTHON ?= python3
PIP ?= pip3

export PYTHONPATH := src
export PYTHONHASHSEED := 0
export OMP_NUM_THREADS := 2
export OPENBLAS_NUM_THREADS := 2
export MKL_NUM_THREADS := 2
export NUMEXPR_NUM_THREADS := 2

.PHONY: install prepare-sources test reproduce preview-visualizations visualize validate validate-visualizations clean-derived

install:
	$(PIP) install -r requirements-lock.txt

prepare-sources:
	$(PYTHON) docs/prepare_gutenberg_additions.py --out-dir data/interim/seed_prepared_text/gutenberg_additions data/raw/translations/Homer_Odyssey_Chapman_PG48895.epub data/raw/translations/Homer_Odyssey_Pope_PG3160.epub data/raw/translations/Homer_Odyssey_Cowper_PG24269.epub data/raw/translations/Homer_Odyssey_Butcher_Lang_PG1728.epub
	$(PYTHON) docs/prepare_retained_texts.py --butler-epub data/raw/translations/Homer_Odyssey_Butler_1900_ProjectGutenberg.epub --murray-vol1 data/raw/translations/Homer_Odyssey_Murray_1919_Vol1.pdf --murray-vol2 data/raw/translations/Homer_Odyssey_Murray_1919_Vol2.pdf --out-dir data/interim/seed_prepared_text/retained_poem_only

test:
	$(PYTHON) -m pytest

reproduce: prepare-sources test
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
