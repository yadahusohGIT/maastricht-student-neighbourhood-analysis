"""Download the CBS 2025 neighbourhood workbook."""

from pathlib import Path

import requests


SOURCE_URL = "https://download.cbs.nl/regionale-kaarten/kwb2025.xlsx"
OUTPUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "kwb2025.xlsx"
)


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(SOURCE_URL, timeout=120)
    response.raise_for_status()
    OUTPUT_PATH.write_bytes(response.content)

    print(f"Downloaded CBS workbook to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
