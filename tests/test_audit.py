
import pandas as pd
import pytest

from src.clean_bibliography import audit_bibliography


def test_clean_records_have_no_quality_issues():
    df = pd.DataFrame({
        "id": ["W1", "W2"],
        "title": ["Paper A", "Paper B"],
        "doi": [
            "https://doi.org/10.1234/a",
            "https://doi.org/10.1234/b",
        ],
        "publication_year": [2021, 2023],
    })

    report = audit_bibliography(df)

    assert report["missing_title"] == 0
    assert report["duplicate_doi_rows"] == 0
    assert report["invalid_publication_year_rows"] == 0


def test_detects_missing_and_blank_values():
    df = pd.DataFrame({
        "id": ["W1", "W2"],
        "title": ["Paper A", "  "],
        "doi": ["10.1234/a", None],
        "publication_year": [2021, 2022],
    })

    report = audit_bibliography(df)

    assert report["missing_title"] == 1
    assert report["missing_doi"] == 1


def test_detects_duplicate_dois_after_normalization():
    df = pd.DataFrame({
        "id": ["W1", "W2"],
        "title": ["Paper A", "Paper B"],
        "doi": [
            "https://doi.org/10.1234/example",
            "10.1234/example",
        ],
        "publication_year": [2021, 2022],
    })

    report = audit_bibliography(df)

    assert report["duplicate_doi_rows"] == 2


def test_detects_invalid_publication_years():
    df = pd.DataFrame({
        "id": ["W1", "W2", "W3"],
        "title": ["Paper A", "Paper B", "Paper C"],
        "doi": ["10.1234/a", "10.1234/b", "10.1234/c"],
        "publication_year": [2019, 2021, "unknown"],
    })

    report = audit_bibliography(df, start_year=2020, end_year=2025)

    assert report["invalid_publication_year_rows"] == 2


def test_missing_required_column_raises_error():
    df = pd.DataFrame({
        "id": ["W1"],
        "title": ["Paper A"],
    })

    with pytest.raises(ValueError, match="Missing required columns"):
        audit_bibliography(df)
