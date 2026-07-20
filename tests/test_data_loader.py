"""
Basic unit tests for src/data_loader.py.
Run with: pytest tests/ -v
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from data_loader import validate_schema, summarize, EXPECTED_COLUMNS


def make_sample_df():
    return pd.DataFrame([
        {
            "record_id": "OBS_001", "record_type": "observation", "pillar": "access",
            "indicator": "Account ownership", "indicator_code": "ACC_OWNERSHIP",
            "value_numeric": 49.0, "observation_date": "2024-01-01",
            "category": None, "source_type": "survey", "source_name": "Global Findex",
            "source_url": "https://worldbank.org/globalfindex", "original_text": "49%",
            "confidence": "high", "parent_id": None, "related_indicator": None,
            "impact_direction": None, "impact_magnitude": None, "lag_months": None,
            "evidence_basis": None, "collected_by": "starter", "collection_date": "2024-01-01",
            "notes": "",
        },
        {
            "record_id": "EVT_001", "record_type": "event", "pillar": None,
            "indicator": None, "indicator_code": None, "value_numeric": None,
            "observation_date": "2021-05-01", "category": "product_launch",
            "source_type": "news", "source_name": "Ethio Telecom", "source_url": "https://ethiotelecom.et",
            "original_text": "Telebirr launched", "confidence": "high", "parent_id": None,
            "related_indicator": None, "impact_direction": None, "impact_magnitude": None,
            "lag_months": None, "evidence_basis": None, "collected_by": "starter",
            "collection_date": "2021-05-01", "notes": "",
        },
        {
            "record_id": "LNK_001", "record_type": "impact_link", "pillar": "usage",
            "indicator": None, "indicator_code": None, "value_numeric": None,
            "observation_date": None, "category": None, "source_type": None,
            "source_name": None, "source_url": None, "original_text": None,
            "confidence": "medium", "parent_id": "EVT_001",
            "related_indicator": "ACC_MM_ACCOUNT", "impact_direction": "positive",
            "impact_magnitude": 5.0, "lag_months": 6,
            "evidence_basis": "comparable country evidence", "collected_by": "starter",
            "collection_date": "2024-01-01", "notes": "",
        },
    ])


def test_expected_columns_defined():
    assert "record_type" in EXPECTED_COLUMNS
    assert "parent_id" in EXPECTED_COLUMNS


def test_validate_schema_no_issues_on_clean_data():
    df = make_sample_df()
    issues = validate_schema(df)
    assert "orphaned_impact_links" not in issues
    assert "duplicate_record_ids" not in issues


def test_validate_schema_detects_orphaned_impact_link():
    df = make_sample_df()
    df.loc[df["record_id"] == "LNK_001", "parent_id"] = "EVT_DOES_NOT_EXIST"
    issues = validate_schema(df)
    assert "orphaned_impact_links" in issues
    assert "LNK_001" in issues["orphaned_impact_links"]


def test_validate_schema_detects_duplicate_ids():
    df = make_sample_df()
    dup = df.iloc[[0]].copy()
    df = pd.concat([df, dup], ignore_index=True)
    issues = validate_schema(df)
    assert "duplicate_record_ids" in issues


def test_summarize_returns_expected_keys():
    df = make_sample_df()
    summary = summarize(df)
    assert "by_record_type" in summary
    assert summary["by_record_type"]["observation"] == 1
    assert summary["by_record_type"]["event"] == 1
    assert summary["by_record_type"]["impact_link"] == 1