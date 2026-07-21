# Ethiopia Financial Inclusion Forecast

Forecasting system tracking Ethiopia's digital financial transformation.
Built for Selam Analytics on behalf of a consortium including the National
Bank of Ethiopia, mobile money operators, and development finance institutions.

Forecasts two Global Findex indicators for 2025-2027:
- **Access** — Account Ownership Rate
- **Usage** — Digital Payment Adoption Rate

## Business Context

Ethiopia's digital financial transformation is being driven by rapid
mobile money growth (Telebirr: 54M+ users, M-Pesa: 10M+ users since 2023),
yet account ownership grew only 3 percentage points between 2021 and 2024
Findex surveys (46% → 49%). This project analyzes what's driving — and
limiting — financial inclusion, and forecasts where it's headed.

## Project Structure

    ethiopia-fi-forecast/
    ├── data/
    │   ├── raw/            # Original starter dataset (unedited)
    │   └── processed/      # Enriched, analysis-ready dataset
    ├── notebooks/          # Task 1-4 analysis notebooks
    ├── src/                # Reusable Python modules
    ├── dashboard/app.py    # Streamlit dashboard (Task 5)
    ├── models/             # Saved forecasting model artifacts
    ├── reports/            # Interim & final written reports + figures
    ├── tests/              # Unit tests
    └── data_enrichment_log.md   # Documentation of all Task 1 additions

## Setup

    python -m venv venv
    source venv/bin/activate      # Windows: venv\Scripts\activate
    pip install -r requirements.txt

## Data

Place the starter dataset in `data/raw/`:
- `ethiopia_fi_unified_data.xlsx` (or .csv)
- `reference_codes.csv`

The loader in `src/data_loader.py` auto-detects file type and handles
both single-sheet and multi-sheet formats.

## Running the Notebooks

    jupyter notebook notebooks/

Run in order:
1. `01_data_exploration.ipynb` — Task 1: schema exploration & enrichment
2. `02_eda.ipynb` — Task 2: EDA covering Access/Usage trends, event timeline,
   correlation analysis, and 5+ key insights
3. `03_impact_modeling.ipynb` — Task 3: event impact modeling
4. `04_forecasting.ipynb` — Task 4: forecasting Access & Usage
## Running the Dashboard

    streamlit run dashboard/app.py

## Running Tests

    pytest tests/ -v

## Methodology Summary

*(fill in as you complete each task — 2-3 sentences each)*
- **Data enrichment:** Enriched the starter dataset with [N] additional
  observations, [N] events, and [N] impact_links sourced from [key sources,
  e.g. NBE, GSMA, Findex microdata]. See `data_enrichment_log.md` for details.
- **EDA key findings:** Account ownership grew from 14% (2011) to 49% (2024)
  but decelerated sharply in 2021-2024 (+3pp) despite Telebirr/M-Pesa mobile
  money expansion — likely reflecting overlap between mobile money and
  existing bank account holders rather than net-new inclusion. [Add 1-2 more
  sentences on your strongest correlation/gender-gap/infrastructure findings.]
- **Impact modeling approach:** ...
- **Forecasting approach:** ...
## Task Status
- [x] Task 1 — Data Exploration & Enrichment
- [x] Task 2 — Exploratory Data Analysis
- [x] Task 3 — Event Impact Modeling
- [ ] Task 4 — Forecasting
- [ ] Task 5 — Dashboard
## Team

Data Scientist: [Your Name]
Challenge: 10 Academy Week 11 — Ethiopia Financial Inclusion Forecasting

## References

- Global Findex Database — worldbank.org/globalfindex
- National Bank of Ethiopia — nbe.gov.et
- See `data_enrichment_log.md` for all enrichment sources