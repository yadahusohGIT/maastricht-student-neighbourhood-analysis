"""Validate the processed dataset."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "neighbourhood_scores.csv"
REPORT = ROOT / "validation" / "validation_report.json"

def main() -> None:
    frame = pd.read_csv(DATA)
    checks = {
        "row_count_is_38": len(frame) == 38,
        "codes_unique": frame["neighbourhood_code"].is_unique,
        "scores_in_range": frame["balanced_score"].between(0, 100).all(),
        "ranks_complete": sorted(frame["balanced_rank"].astype(int)) == list(range(1, 39)),
        "core_fields_complete": frame[["neighbourhood", "population", "housing_units", "rental_housing_pct", "student_age_share_pct", "balanced_score"]].notna().all().all(),
        "one_imputed_supermarket_value": frame["supermarket_distance_imputed"].sum() == 1,
    }
    report = {"status": "passed" if all(checks.values()) else "failed", "checks": checks}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not all(checks.values()):
        raise AssertionError(report)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
