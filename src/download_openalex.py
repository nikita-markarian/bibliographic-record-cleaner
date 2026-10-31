import os
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://api.openalex.org/works"
SOURCE_ID = "S45918994"
START_YEAR = 2020
END_YEAR = 2025

FIELDS = [
    "id",
    "doi",
    "title",
    "publication_year",
    "publication_date",
    "type",
    "is_retracted",
    "authorships",
    "primary_location",
    "biblio",
    "language",
    "cited_by_count",
]


def download_records():
    records = []
    cursor = "*"
    api_key = os.environ.get("OPENALEX_API_KEY")

    while cursor:
        params = {
            "filter": (
                f"primary_location.source.id:{SOURCE_ID},"
                f"publication_year:{START_YEAR}-{END_YEAR},"
                "type:article"
            ),
            "select": ",".join(FIELDS),
            "per_page": 100,
            "cursor": cursor,
        }
        
        api_key = os.environ.get("OPENALEX_API_KEY")
        if api_key:
            params["api_key"] = api_key        
        
        url = f"{API_URL}?{urllib.parse.urlencode(params)}"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "bibliographic-record-cleaner/0.1"},
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)

        records.extend(data["results"])
        cursor = data["meta"].get("next_cursor")

        print(f"Retrieved {len(records)} records so far")

        if cursor:
            time.sleep(0.1)

    return records


def main():
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / "data" / "annals_2020_2025.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    records = download_records()

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()

        for record in records:
            row = {}
            for field in FIELDS:
                value = record.get(field)
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                row[field] = value
            writer.writerow(row)

    print(f"Saved {len(records)} records to {output_path}")


if __name__ == "__main__":
    main()
