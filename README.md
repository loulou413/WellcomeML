# Embedded Space Visualization & Metadata Enrichment for Wellcome Collection Datasets

**Primary goal: retrieve, clean, and enrich Wellcome Collection catalogue records.**  

This project focuses on obtaining dataset snapshots and improving metadata quality by filling missing or inconsistent fields (dates, locations, subjects, creators) using deterministic heuristics, text inference, and record linking.

Key capabilities:
- Download and version dataset snapshots from the Wellcome API or provided JSON/CSV dumps.
- Clean and normalize metadata fields (dates, names, locations, subject tags).
- Enrich / impute missing values using internal data, rule-based inference, and cross-record linking.

---

## Content

- `data/` – raw snapshots and cleaned/enriched outputs  
- `scripts/` – downloader, cleaning, enrichment, and export utilities  
- `notebooks/` – optional exploratory notebooks for analysis and visualization  
- `results/` – visualizations, reports, and export-ready CSV/JSON  
- `README.md` – Project overview (this file)

---

## Project Workflow

1. Retrieve a dataset snapshot (Wellcome catalogue).
2. Normalize fields (dates, creators, locations, subject tags).
3. Identify empty or ambiguous fields and attempt to fill them via:
    - Text inference from title/description/notes
    - Controlled-vocabulary matching for subjects and locations
    - Cross-record linking and de-duplication
    - Optional external lookups (respecting terms and privacy)
4. Validate and log changes with provenance metadata.


---

## Data Sources

| Dataset | Focus | Link |
|---------|-------|------|
| Catalogue snapshot (primary) | Metadata for Wellcome Collection works and images — target for enrichment | https://developers.wellcomecollection.org/docs/datasets/catalogue |

Note: External lookups are used only when terms/permissions allow.

---

## Installation

```bash
git clone https://github.com/loulou413/WellcomeML.git
cd WellcomeML

python -m venv <env_name>
source <env_name>/bin/activate    # Windows: <env_name>\Scripts\activate

pip install -r requirements.txt
```

---

## Usage (brief)

- Use `scripts/download_catalogue.py` to fetch a snapshot (or place your JSON/CSV in `data/raw/`).
- Run `scripts/clean_metadata.py` to normalize fields.
- Run `scripts/enrich_metadata.py` to attempt filling empty fields (outputs saved in `data/enriched/`).
- Optional: explore `notebooks/` for lightweight analyses and visual checks (embeddings/UMAP/t-SNE/PCA only if needed).

Contributions, issues, and suggestions are welcome via the repository.
