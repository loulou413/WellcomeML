# Embedded Space Visualization for Wellcome Collection Datasets

**Explore, understand, and visualize high-dimensional representations of cultural and medical data.**

This project applies machine learning embedding methods and dimensionality reduction visualization (t-SNE, UMAP, PCA) to the public datasets available through the [Wellcome Collection Developer API & Datasets](https://developers.wellcomecollection.org/docs/datasets).

The goal is to transform textual and metadata-rich records (e.g. catalogue works, medical reports) into semantic vector spaces and produce interactive visualizations to explore patterns, clusters, and relationships.

---

## Content

- `data/` – Scripts for downloading and cleaning Wellcome datasets  
- `README.md` – Project overview (you’re reading it!)

---

## Project Overview

## Data Sources

| Dataset | Description | Link |
|----------|--------------|------|
| Catalogue snapshot | Metadata for Wellcome Collection’s works and images | [Wellcome Works Dataset](https://developers.wellcomecollection.org/docs/datasets/catalogue) |
| London MOH Reports | Medical Officer of Health annual reports (1850–1972) | [MOH Reports Dataset](https://developers.wellcomecollection.org/docs/datasets/moh-reports) |

You can access them via the **Wellcome API** or download the snapshots directly (JSON or CSV).


---

## Installation

```bash
git clone https://github.com/loulou413/WellcomeML.git
cd WellcomeML

python -m venv <environement name>
source <environement name>/bin/activate    # or on Windows: <environement name>\Scripts\activate

pip install -r requirements.txt
