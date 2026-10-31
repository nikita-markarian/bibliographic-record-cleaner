
from pathlib import Path

import pandas as pd

from src.clean_bibliography import audit_bibliography


def main():
    # Find the project directory, regardless of where we run the script from.
    project_dir = Path(__file__).resolve().parent.parent

    # Locate the input CSV file.
    csv_path = project_dir / "data" / "annals_2020_2025.csv"

    # Read the bibliographic records.
    df = pd.read_csv(csv_path)

    # Run the quality checks.
    report = audit_bibliography(df)

    # Display the results.
    print(f"Records audited: {len(df)}")
    print("\nBibliographic quality report:")
    for check, count in report.items():
        print(f"{check}: {count}")


if __name__ == "__main__":
    main()
