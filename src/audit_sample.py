
import csv
import json
import os
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


STRASBOURG_ID = "https://openalex.org/I68947357"

INPUT_PATH = Path("data/strasbourg_sample.json")
OUTPUT_PATH = Path("data/audit_results.csv")


def fetch_full_work(work):
    """Retrieve a complete OpenAlex work record."""
    work_id = work["id"]
    url = work_id.replace(
        "https://openalex.org/",
        "https://api.openalex.org/works/",
    )

    api_key = os.environ.get("OPENALEX_API_KEY")
    if api_key:
        url += "?" + urlencode({"api_key": api_key})

    try:
        with urlopen(url, timeout=30) as response:
            return json.load(response)

    except HTTPError as error:
        print(f"OpenAlex HTTP error {error.code}: {work_id}")
    except URLError as error:
        print(f"Network error for {work_id}: {error.reason}")
    except TimeoutError:
        print(f"Request timed out for {work_id}")

    return None


def count_strasbourg_authorships(work):
    """Count authorships associated with Strasbourg."""
    return sum(
        1
        for authorship in work.get("authorships") or []
        if any(
            institution.get("id") == STRASBOURG_ID
            for institution in authorship.get("institutions") or []
        )
    )


def classify_affiliation(work):
    """Classify institutional affiliation evidence."""
    if count_strasbourg_authorships(work) > 0:
        return "confirmed"

    if len(work.get("authorships") or []) == 100:
        return "needs_review"

    return "suspicious"


def load_works(path):
    """Load publications from a JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        return data["results"]

    raise TypeError(f"Unexpected JSON structure: {type(data)}")


works = load_works(INPUT_PATH)
results = []

print(f"Auditing {len(works)} works\n")

for work in works:
    title = work.get("title")
    year = work.get("publication_year")
    doi = work.get("doi")

    audited_work = work
    status = classify_affiliation(work)

    if status == "needs_review":
        full_work = fetch_full_work(work)

        if full_work is None:
            status = "verification_failed"
        else:
            audited_work = full_work

            if classify_affiliation(full_work) == "confirmed":
                status = "confirmed_after_verification"
            else:
                status = "suspicious"

    strasbourg_count = count_strasbourg_authorships(audited_work)

    issues = []

    if not title:
        issues.append("missing title")
    if not doi:
        issues.append("missing DOI")
    if not year:
        issues.append("missing publication year")

    if status == "suspicious":
        issues.append("Strasbourg affiliation not found; investigate")
    elif status == "verification_failed":
        issues.append("Could not retrieve full record")

    results.append({
        "title": title,
        "year": year,
        "doi": doi,
        "strasbourg_authorships": strasbourg_count,
        "affiliation_status": status,
        "issues": "; ".join(issues),
    })

    print(f"Title: {title or '(missing title)'}")
    print(f"Year: {year}")
    print(f"DOI: {doi or 'MISSING'}")
    print(f"Strasbourg authorships: {strasbourg_count}")
    print(f"Affiliation status: {status}")
    print("Checks:", "; ".join(issues) if issues else "no issues detected")
    print("-" * 60)


OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "title",
            "year",
            "doi",
            "strasbourg_authorships",
            "affiliation_status",
            "issues",
        ],
    )
    writer.writeheader()
    writer.writerows(results)


status_counts = Counter(
    result["affiliation_status"]
    for result in results
)

print("\n=== AUDIT SUMMARY ===")
print(f"Total publications: {len(results)}")

for status, count in sorted(status_counts.items()):
    print(f"{status}: {count}")

print(f"\nAudit results saved to {OUTPUT_PATH}")

