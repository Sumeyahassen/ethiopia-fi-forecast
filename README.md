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

### Running the Notebooks

    jupyter notebook notebooks/

Run in order:
1. `01_data_exploration.ipynb` — Task 1: schema exploration & enrichment
2. `02_eda.ipynb` — Task 2: EDA covering Access/Usage trends, event timeline,
   correlation analysis, and 5+ key insights
3. `03_impact_modeling.ipynb` — Task 3: event-indicator impact matrix,
   validated against observed mobile money growth
4. `04_forecasting.ipynb` — Task 4: Access & Usage forecasts for 2025-2027
   with pessimistic/base/optimistic scenarios (saved to `models/forecast_models.pkl`)## Running the Dashboard

    streamlit run dashboard/app.py

## Running Tests

    pytest tests/ -v
## Running the Dashboard

    streamlit run dashboard/app.py

Run this command from the project root directory. The dashboard requires
`data/processed/ethiopia_fi_enriched.csv` and `models/forecast_models.pkl`
to exist — run notebooks 01 through 04 first if these are missing.

The dashboard has 4 pages (use the sidebar to navigate):
- **Overview** — key metrics, growth rates, data composition
- **Trends** — interactive indicator comparison with date range filter
- **Forecasts** — Access & Usage projections with confidence scenarios
- **Inclusion Projections** — scenario selector, policy target progress
## Methodology Summary

- **Data enrichment:** Enriched the starter dataset (57 records) with
  additional observations, events, and impact_links sourced from NBE, GSMA,
  and Findex materials, including a missing Telebirr→mobile money impact
  link identified during validation. See `data_enrichment_log.md`.
- **EDA key findings:** Account ownership grew from 14% (2011) to 49% (2024)
  but decelerated sharply in 2021-2024 (+3pp) despite Telebirr/M-Pesa mobile
  money expansion — likely reflecting overlap between mobile money and
  existing bank account holders rather than net-new inclusion.
- **Impact modeling approach:** Modeled event effects using a logistic
  ramp-up function with magnitude estimates derived from qualitative
  high/medium/low labels (5pp/2.5pp/1pp). Validated against observed mobile
  money growth (2021-2024): modeled +5.00pp vs actual +4.75pp.
- **Forecasting approach:** Access forecast anchored to the recent
  (2021-2024) observed growth rate (~1.0pp/year) rather than full-history
  OLS, since OLS on the full 2011-2024 range overstated near-term growth
  by averaging in faster early-period gains. Usage forecast anchored to the
  2024 Findex figure (35%) and projected using mobile money's percentage-
  point growth rate as a proxy, since no multi-year Usage time series
  existed in the dataset. Event effects were added incrementally (only
  the portion not already reflected in historical data) to avoid double-
  counting. Base case: Access 49.2%→53.6% and Usage 35.8%→39.1% by 2027,
  with pessimistic/optimistic scenario bands.
## Task Status
- [x] Task 1 — Data Exploration & Enrichment
- [x] Task 2 — Exploratory Data Analysis
- [x] Task 3 — Event Impact Modeling
- [x] Task 4 — Forecasting
- [ ] Task 5 — Dashboard
## Team

Data Scientist: [Your Name]
Challenge: 10 Academy Week 11 — Ethiopia Financial Inclusion Forecasting

## References

- Global Findex Database — worldbank.org/globalfindex
- National Bank of Ethiopia — nbe.gov.et
- See `data_enrichment_log.md` for all enrichment sources