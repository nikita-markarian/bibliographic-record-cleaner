# Bibliographic Record Cleaner

A Python project for cleaning, validating, and auditing bibliographic metadata, including publication records retrieved from OpenAlex.

## Features

- DOI normalization and exact duplicate detection.
- Checks for missing titles, DOIs, and publication years.
- Retrieval of publication metadata from the OpenAlex API.
- Verification of institutional affiliations using complete publication records.
- Export of audit results to CSV.
- Automated tests using pytest.

## OpenAlex Affiliation Audit

The project includes an audit of publications associated with the University of Strasbourg (OpenAlex institution ID: `I68947357`).

During development, an important data-quality issue was identified: OpenAlex search results returned only 100 authorships for some large scientific collaborations, while retrieving the individual publications returned more complete authorship lists.

For example:

| Publication | Initial authorships | Full authorships |
|---|---:|---:|
| GWTC-3 | 100 | 1,654 |
| GWTC-2.1 | 100 | 1,431 |

Both publications contained Strasbourg-affiliated authors in their full records.

The audit therefore retrieves individual records when an affiliation is not found in a potentially incomplete authorship list, avoiding false warnings.

## Project Structure

```text
src/
    clean_bibliography.py
    download_openalex.py
    run_audit.py
    inspect_strasbourg.py
    audit_sample.py

tests/
    test_audit.py
    test_duplicates.py

data/
    sample_publications.csv

pytest.ini
README.md
```

## Requirements

- Python 3
- pandas
- pytest (for running tests)
- An OpenAlex API key if required by the API

Set the `OPENALEX_API_KEY` environment variable to provide an API key.

## Usage

Run the Strasbourg publication retrieval:

```bash
python src/inspect_strasbourg.py
```

This saves a sample of 100 publications from 2023–2025 to `data/strasbourg_sample.json`.

Run the affiliation audit:

```bash
python src/audit_sample.py
```

The results are saved to `data/audit_results.csv`.

Run the automated tests:

```bash
python -m pytest -q
```

## Example Results

In a sample of 100 Strasbourg-associated publications:

| Affiliation status | Records |
|---|---:|
| Confirmed directly | 90 |
| Confirmed after full-record verification | 10 |
| Unresolved | 0 |

These results describe one sample and may change as OpenAlex updates its data.

## Limitations

- The affiliation audit currently processes a sample of 100 records, not the complete institutional publication collection.
- The rule treating exactly 100 returned authorships as potentially incomplete is a heuristic.
- Network error handling is implemented for full-record verification but not for every API request.
- The tool is a proof of concept rather than a production bibliometric system.

## Data Source

Publication metadata is retrieved from [OpenAlex](https://openalex.org/), an open catalog of scholarly works, authors, institutions, and related research information.
