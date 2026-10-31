from src.clean_bibliography import normalize_doi


def test_normalize_doi():
    assert normalize_doi("https://doi.org/10.1234/ABC") == "10.1234/abc"
    assert normalize_doi("doi:10.1234/ABC") == "10.1234/abc"
    assert normalize_doi("  10.1234/ABC  ") == "10.1234/abc"
    assert normalize_doi("") == ""
    assert normalize_doi(None) == ""


def test_normalize_doi_case_insensitive():
    assert normalize_doi("10.1234/ABC") == normalize_doi("10.1234/abc")

import pandas as pd

from src.clean_bibliography import (
    normalize_doi,
    find_exact_duplicates,
)


def test_find_exact_duplicates():
    df = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "title": ["Paper A", "Paper A", "Paper B", "Paper C"],
        "doi": [
            "10.1234/ABC",
            "https://doi.org/10.1234/ABC",
            "10.5678/DEF",
            "",
        ],
    })

    result = find_exact_duplicates(df)

    assert set(result["id"]) == {1, 2}
