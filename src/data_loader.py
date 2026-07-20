"""
data_loader.py
Loading and validation utilities for the Ethiopia Financial Inclusion
unified dataset (Task 1).

The unified schema stores four record types in one table:
    - observation : measured values (Findex, operator reports, infra data)
    - event        : policies, product launches, market entries, milestones
    - impact_link  : modeled relationships between events and indicators
    - target       : official policy goals

Some source files split "data" (observation/event/target) and
"impact_links" (impact_link) into separate sheets. These functions
handle both a single unified file and a two-sheet workbook.
"""

from pathlib import Path
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

EXPECTED_COLUMNS = [
    "record_id",
    "record_type",       # observation | event | impact_link | target
    "pillar",             # access | usage | (empty for events)
    "indicator",
    "indicator_code",
    "value_numeric",
    "observation_date",
    "category",            # event category, e.g. policy, product_launch, infrastructure
    "source_type",
    "source_name",
    "source_url",
    "original_text",
    "confidence",           # high | medium | low
    "parent_id",             # links impact_link -> event record_id
    "related_indicator",
    "impact_direction",
    "impact_magnitude",
    "lag_months",
    "evidence_basis",
    "collected_by",
    "collection_date",
    "notes",
]


def _find_raw_file(preferred_names):
    """Return the first matching file found in data/raw for a list of
    candidate filenames (checks .csv, .xlsx, .xls extensions)."""
    for name in preferred_names:
        for ext in (".csv", ".xlsx", ".xls"):
            candidate = RAW_DIR / f"{name}{ext}"
            if candidate.exists():
                return candidate
    # fallback: any csv/xlsx in raw dir
    for ext in ("*.csv", "*.xlsx", "*.xls"):
        matches = list(RAW_DIR.glob(ext))
        if matches:
            return matches[0]
    return None


def _read_csv_robust(filepath):
    """
    Read a CSV trying multiple encodings, and auto-detect the delimiter
    (comma, semicolon, or tab) since Excel exports vary by locale.
    """
    encodings_to_try = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
    last_error = None

    for enc in encodings_to_try:
        try:
            df = pd.read_csv(filepath, encoding=enc, sep=None, engine="python")
            print(f"[data_loader] Loaded '{filepath.name}' using encoding='{enc}' (auto-detected separator)")
            return df
        except UnicodeDecodeError as e:
            last_error = e
            continue

    raise UnicodeDecodeError(
        f"Could not read {filepath} with any of {encodings_to_try}. "
        f"Last error: {last_error}"
    ) # type: ignore
def load_unified_data(filepath=None):
    """
    Load the unified financial inclusion dataset.

    Handles three cases:
      1. A single CSV/XLSX with one sheet containing all record_types.
      2. An XLSX with multiple sheets, e.g. 'data' and 'impact_links' —
         these are concatenated into one unified DataFrame.
      3. An explicit filepath passed in.

    Returns
    -------
    pd.DataFrame
        Unified dataframe with all record types stacked, columns
        aligned to EXPECTED_COLUMNS where present.
    """
    if filepath is None:
        filepath = _find_raw_file(["ethiopia_fi_unified_data", "ethiopia_fi_data"])
        if filepath is None:
            raise FileNotFoundError(
                f"No unified dataset found in {RAW_DIR}. "
                "Expected a file like 'ethiopia_fi_unified_data.csv' or .xlsx"
            )
    else:
        filepath = Path(filepath)

    if filepath.suffix.lower() == ".csv":
        df = _read_csv_robust(filepath)
        return _postprocess(df)

    # Excel: check for multiple relevant sheets
    xl = pd.ExcelFile(filepath)

    frames = []
    for sheet in xl.sheet_names:
        frames.append(pd.read_excel(filepath, sheet_name=sheet))

    if len(frames) == 1:
        df = frames[0]
    else:
        # Concatenate all sheets; assumes each sheet uses the same unified
        # schema (e.g. sheet 1 = data, sheet 2 = impact_links)
        df = pd.concat(frames, ignore_index=True, sort=False)

    return _postprocess(df)


def load_reference_codes(filepath=None):
    """Load the reference_codes lookup table (valid values per field)."""
    if filepath is None:
        filepath = _find_raw_file(["reference_codes"])
        if filepath is None:
            raise FileNotFoundError(f"No reference_codes file found in {RAW_DIR}")
    else:
        filepath = Path(filepath)

    if filepath.suffix.lower() == ".csv":
        return _read_csv_robust(filepath)
    return pd.read_excel(filepath)


def _postprocess(df):
    """Normalize column names, parse dates, coerce numerics."""
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    for date_col in ("observation_date", "collection_date"):
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    if "value_numeric" in df.columns:
        df["value_numeric"] = pd.to_numeric(df["value_numeric"], errors="coerce")

    if "record_type" in df.columns:
        df["record_type"] = df["record_type"].str.strip().str.lower()

    return df


def validate_schema(df, reference_codes=None):
    """
    Run basic sanity checks on the loaded dataset and return a dict
    summary of issues found. Does not raise — meant for exploratory use.
    """
    issues = {}

    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        issues["missing_columns"] = missing_cols

    if "record_type" in df.columns:
        valid_types = {"observation", "event", "impact_link", "target"}
        found_types = set(df["record_type"].dropna().unique())
        unexpected = found_types - valid_types
        if unexpected:
            issues["unexpected_record_types"] = list(unexpected)

    if "record_id" in df.columns:
        dupes = df["record_id"][df["record_id"].duplicated(keep=False)]
        if not dupes.empty:
            issues["duplicate_record_ids"] = dupes.tolist()

    # impact_link rows should have a parent_id that exists elsewhere in the data
    if {"record_type", "parent_id", "record_id"}.issubset(df.columns):
        links = df[df["record_type"] == "impact_link"]
        valid_ids = set(df["record_id"].dropna())
        orphaned = links[~links["parent_id"].isin(valid_ids)]
        if not orphaned.empty:
            issues["orphaned_impact_links"] = orphaned["record_id"].tolist()

    return issues


def summarize(df):
    """Quick summary counts used throughout Task 1 exploration."""
    summary = {}
    if "record_type" in df.columns:
        summary["by_record_type"] = df["record_type"].value_counts(dropna=False)
    if "pillar" in df.columns:
        summary["by_pillar"] = df["pillar"].value_counts(dropna=False)
    if "source_type" in df.columns:
        summary["by_source_type"] = df["source_type"].value_counts(dropna=False)
    if "confidence" in df.columns:
        summary["by_confidence"] = df["confidence"].value_counts(dropna=False)
    if "indicator_code" in df.columns:
        summary["by_indicator_code"] = df["indicator_code"].value_counts(dropna=False)
    return summary


if __name__ == "__main__":
    data = load_unified_data()
    print(f"Loaded {len(data)} records from data/raw/")
    print(data["record_type"].value_counts())

    issues = validate_schema(data)
    if issues:
        print("\nSchema issues found:")
        for k, v in issues.items():
            print(f"  {k}: {v}")
    else:
        print("\nNo schema issues found.")