import pandas as pd


def normalize_doi(doi):
    """Normalize a DOI by removing its URL prefix and whitespace."""
    if pd.isna(doi):
        return ""

    doi = str(doi).strip()

    if not doi:
        return ""

    prefixes = [
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    ]

    for prefix in prefixes:
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix):]
            break

    return doi.strip().lower()


def find_exact_duplicates(df):
    """Return records sharing a non-empty normalized DOI."""
    if "doi" not in df.columns:
        raise ValueError("Missing required column: doi")    

    df = df.copy()
    df["normalized_doi"] = df["doi"].apply(normalize_doi)

    has_doi = df["normalized_doi"] != ""

    duplicates = df[has_doi].duplicated(
        subset=["normalized_doi"],
        keep=False,
    )

    return df[has_doi & duplicates]



def audit_bibliography(df, start_year=2020, end_year=2025):
    """Return a dictionary of basic bibliographic quality checks."""
    required_columns = [
        "id",
        "title",
        "doi",
        "publication_year",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    report = {}

    # Completeness: count missing or blank values.
    for column in required_columns:
        values = df[column]
        missing = values.isna() | values.astype(str).str.strip().eq("")
        report[f"missing_{column}"] = int(missing.sum())

    # Uniqueness: count repeated identifiers.
    for column in ["id", "title"]:
        values = df[column].astype("string").str.strip()
        present = values.notna() & values.ne("")
        report[f"duplicate_{column}_rows"] = int(
            values[present].duplicated(keep=False).sum()
        )

    # DOI duplicates after normalization.
    normalized_dois = df["doi"].apply(normalize_doi)
    has_doi = normalized_dois.ne("")
    report["duplicate_doi_rows"] = int(
        normalized_dois[has_doi].duplicated(keep=False).sum()
    )

    # Validity: publication year must be numeric and in range.
    years = pd.to_numeric(df["publication_year"], errors="coerce")
    valid_years = years.between(start_year, end_year)
    report["invalid_publication_year_rows"] = int(
        (~valid_years).sum()
    )

    return report

