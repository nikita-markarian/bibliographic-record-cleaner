
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


BASE_URL = "https://api.openalex.org/works"
INSTITUTION_ID = "I68947357"
OUTPUT_PATH = Path("data/strasbourg_sample.json")


def main():
    params = {
        "filter": (
            f"institutions.id:{INSTITUTION_ID},"
            "from_publication_date:2023-01-01,"
            "to_publication_date:2025-12-31"
        ),
        "select": (
            "id,doi,title,publication_year,publication_date,"
            "type,authorships"
        ),
        "per_page": 100,
    }

    api_key = os.environ.get("OPENALEX_API_KEY")
    if api_key:
        params["api_key"] = api_key

    url = f"{BASE_URL}?{urlencode(params)}"

    with urlopen(url, timeout=30) as response:
        data = json.load(response)

    works = data["results"]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as output_file:
        json.dump(works, output_file, ensure_ascii=False, indent=2)

    print(f"Total matching works: {data['meta']['count']}")
    print(f"Records retrieved: {len(works)}")
    print(f"Sample saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

