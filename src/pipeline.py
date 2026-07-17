"""Create the Maastricht neighbourhood scoring dataset."""

from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd

from scoring import PROFILES, robust_minmax, weighted_score


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "raw" / "kwb2025.xlsx"
OUTPUT_CSV = ROOT / "data" / "processed" / "neighbourhood_scores.csv"
OUTPUT_DATABASE = (
    ROOT / "data" / "processed" / "maastricht_neighbourhoods.sqlite"
)

MINIMUM_POPULATION = 250
MINIMUM_HOUSING_UNITS = 100

COLUMN_NAMES = {
    "gwb_code_10": "neighbourhood_code",
    "regio": "neighbourhood",
    "a_inw": "population",
    "a_15_24": "residents_15_24",
    "a_25_44": "residents_25_44",
    "a_hh": "households",
    "a_1p_hh": "one_person_households",
    "a_woning": "housing_units",
    "g_wozbag": "average_woz_eur_thousands",
    "p_huurw": "rental_housing_pct",
    "p_mgezw": "apartment_housing_pct",
    "g_afs_gs": "distance_large_supermarket_km",
    "g_pau_hh": "cars_per_household",
    "bev_dich": "population_density_per_km2",
}


def load_source(path: Path) -> pd.DataFrame:
    """Read the CBS workbook."""
    if not path.exists():
        raise FileNotFoundError(
            f"{path} does not exist. Run `python src/download_data.py` first."
        )

    return pd.read_excel(path, sheet_name="KWB2025")


def select_maastricht_neighbourhoods(source: pd.DataFrame) -> pd.DataFrame:
    """Select neighbourhood-level rows for the municipality of Maastricht."""
    maastricht = source.loc[
        (source["gm_naam"].astype(str).str.strip() == "Maastricht")
        & (source["recs"] == "Buurt")
    ].copy()

    selected = maastricht.rename(columns=COLUMN_NAMES)[
        list(COLUMN_NAMES.values())
    ].copy()

    text_columns = {"neighbourhood_code", "neighbourhood"}
    for column in selected.columns:
        if column not in text_columns:
            selected[column] = pd.to_numeric(
                selected[column],
                errors="coerce",
            )

    return selected


def calculate_neighbourhood_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Create the percentages used by the scoring model."""
    result = frame.copy()

    result["student_age_share_pct"] = (
        100 * result["residents_15_24"] / result["population"]
    )
    result["young_adult_share_pct"] = (
        100
        * (result["residents_15_24"] + result["residents_25_44"])
        / result["population"]
    )
    result["one_person_household_pct"] = (
        100 * result["one_person_households"] / result["households"]
    )

    return result


def keep_residential_neighbourhoods(frame: pd.DataFrame) -> pd.DataFrame:
    """Remove very small areas whose percentages are likely to be unstable."""
    return frame.loc[
        (frame["population"] >= MINIMUM_POPULATION)
        & (frame["housing_units"] >= MINIMUM_HOUSING_UNITS)
    ].copy()


def handle_missing_values(frame: pd.DataFrame) -> pd.DataFrame:
    """Impute the one missing supermarket-distance value and keep a flag."""
    result = frame.copy()
    missing_distance = result["distance_large_supermarket_km"].isna()

    result["supermarket_distance_imputed"] = missing_distance
    result["distance_large_supermarket_km"] = result[
        "distance_large_supermarket_km"
    ].fillna(result["distance_large_supermarket_km"].median())

    return result


def add_component_scores(frame: pd.DataFrame) -> pd.DataFrame:
    """Convert the six model inputs to comparable 0-100 scores."""
    result = frame.copy()

    result["component_student_presence"] = robust_minmax(
        result["student_age_share_pct"]
    )
    result["component_rental_access"] = robust_minmax(
        result["rental_housing_pct"]
    )
    result["component_apartment_fit"] = robust_minmax(
        result["apartment_housing_pct"]
    )
    result["component_single_household_fit"] = robust_minmax(
        result["one_person_household_pct"]
    )
    result["component_cost_proxy"] = robust_minmax(
        result["average_woz_eur_thousands"],
        invert=True,
    )
    result["component_grocery_access"] = robust_minmax(
        result["distance_large_supermarket_km"],
        invert=True,
    )

    return result


def add_profile_scores(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate each preference profile and its rank."""
    result = frame.copy()

    for profile_name, weights in PROFILES.items():
        score_column = f"{profile_name}_score"
        rank_column = f"{profile_name}_rank"

        result[score_column] = weighted_score(result, weights).round(1)
        result[rank_column] = (
            result[score_column]
            .rank(method="min", ascending=False)
            .astype(int)
        )

    return result.sort_values("balanced_rank").reset_index(drop=True)


def build_dataset(path: Path = INPUT_PATH) -> pd.DataFrame:
    """Run the complete transformation pipeline."""
    source = load_source(path)
    neighbourhoods = select_maastricht_neighbourhoods(source)
    neighbourhoods = calculate_neighbourhood_metrics(neighbourhoods)
    neighbourhoods = keep_residential_neighbourhoods(neighbourhoods)
    neighbourhoods = handle_missing_values(neighbourhoods)
    neighbourhoods = add_component_scores(neighbourhoods)
    neighbourhoods = add_profile_scores(neighbourhoods)

    return neighbourhoods


PUBLIC_COLUMNS = [
    "neighbourhood_code",
    "neighbourhood",
    "population",
    "housing_units",
    "student_age_share_pct",
    "one_person_household_pct",
    "rental_housing_pct",
    "apartment_housing_pct",
    "average_woz_eur_thousands",
    "distance_large_supermarket_km",
    "supermarket_distance_imputed",
    "balanced_score",
    "balanced_rank",
    "budget_focused_score",
    "budget_focused_rank",
    "student_hub_score",
    "student_hub_rank",
    "housing_availability_score",
    "housing_availability_rank",
]


def write_outputs(frame: pd.DataFrame) -> None:
    """Write a compact public CSV and a fuller SQLite database."""
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    frame[PUBLIC_COLUMNS].to_csv(OUTPUT_CSV, index=False)

    with sqlite3.connect(OUTPUT_DATABASE) as connection:
        frame.to_sql(
            "neighbourhood_scores",
            connection,
            if_exists="replace",
            index=False,
        )


def main() -> None:
    result = build_dataset()
    write_outputs(result)

    print(f"Wrote {len(result)} neighbourhoods to {OUTPUT_CSV}")
    print(f"Wrote SQLite database to {OUTPUT_DATABASE}")


if __name__ == "__main__":
    main()
