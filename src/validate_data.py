"""Run basic data-quality and regression checks."""

from __future__ import annotations

from pathlib import Path
import json
import math

import pandas as pd

from scoring import PROFILES


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "neighbourhood_scores.csv"
REPORT_PATH = ROOT / "validation" / "validation_report.json"

EXPECTED_ROW_COUNT = 38
CORE_COLUMNS = [
    "neighbourhood_code",
    "neighbourhood",
    "population",
    "housing_units",
    "student_age_share_pct",
    "rental_housing_pct",
    "apartment_housing_pct",
    "average_woz_eur_thousands",
    "balanced_score",
]


def main() -> None:
    frame = pd.read_csv(DATA_PATH)

    checks = {
        "dataset_not_empty": len(frame) > 0,
        "neighbourhood_codes_unique": frame[
            "neighbourhood_code"
        ].is_unique,
        "core_fields_complete": frame[CORE_COLUMNS].notna().all().all(),
        "population_positive": (frame["population"] > 0).all(),
        "housing_units_positive": (frame["housing_units"] > 0).all(),
        "percentage_fields_in_range": frame[
            [
                "student_age_share_pct",
                "rental_housing_pct",
                "apartment_housing_pct",
                "one_person_household_pct",
            ]
        ].apply(lambda column: column.between(0, 100).all()).all(),
        "profile_scores_in_range": frame[
            [f"{name}_score" for name in PROFILES]
        ].apply(lambda column: column.between(0, 100).all()).all(),
        "balanced_ranks_contiguous": sorted(
            frame["balanced_rank"].astype(int).tolist()
        )
        == list(range(1, len(frame) + 1)),
        "weights_sum_to_one": all(
            math.isclose(sum(weights.values()), 1.0, abs_tol=1e-9)
            for weights in PROFILES.values()
        ),
        "imputed_values_flagged": (
            frame.loc[
                frame["supermarket_distance_imputed"].astype(bool),
                "distance_large_supermarket_km",
            ].notna().all()
        ),
    }

    warnings = []
    if len(frame) != EXPECTED_ROW_COUNT:
        warnings.append(
            "The row count changed from the 2025 snapshot "
            f"({EXPECTED_ROW_COUNT}) to {len(frame)}. "
            "Check whether CBS revised the source."
        )

    report = {
        "status": "passed" if all(checks.values()) else "failed",
        "rows": len(frame),
        "checks": {name: bool(value) for name, value in checks.items()},
        "warnings": warnings,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    if report["status"] == "failed":
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"Validation failed: {failed}")

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
