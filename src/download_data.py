"""Download the CBS 2025 neighbourhood workbook."""
from pathlib import Path
import requests

URL = "https://download.cbs.nl/regionale-kaarten/kwb2025.xlsx"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "kwb2025.xlsx"

def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(URL, timeout=120)
    response.raise_for_status()
    OUTPUT.write_bytes(response.content)
    print(f"Downloaded to {OUTPUT}")

if __name__ == "__main__":
    main()
