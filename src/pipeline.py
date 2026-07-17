"""Rebuild the scored dataset from the downloaded CBS workbook."""
from pathlib import Path
import sqlite3
import pandas as pd
from scoring import PROFILES, robust_minmax, weighted_score

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "kwb2025.xlsx"
OUTPUT = ROOT / "data" / "processed" / "neighbourhood_scores.csv"
DATABASE = ROOT / "data" / "processed" / "maastricht_neighbourhoods.sqlite"

def build_dataset() -> pd.DataFrame:
    source = pd.read_excel(INPUT, sheet_name="KWB2025")
    frame = source.loc[(source["gm_naam"].astype(str).str.strip() == "Maastricht") & (source["recs"] == "Buurt")].copy()
    rename = {
        "gwb_code_10": "neighbourhood_code", "regio": "neighbourhood",
        "a_inw": "population", "a_15_24": "residents_15_24",
        "a_25_44": "residents_25_44", "a_hh": "households",
        "a_1p_hh": "one_person_households", "a_woning": "housing_units",
        "g_wozbag": "average_woz_eur_thousands", "p_huurw": "rental_housing_pct",
        "p_mgezw": "apartment_housing_pct", "g_afs_gs": "distance_large_supermarket_km",
        "g_pau_hh": "cars_per_household", "bev_dich": "population_density_per_km2",
    }
    frame = frame.rename(columns=rename)[list(rename.values())]
    for column in frame.columns:
        if column not in {"neighbourhood_code", "neighbourhood"}:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["student_age_share_pct"] = 100 * frame["residents_15_24"] / frame["population"]
    frame["young_adult_share_pct"] = 100 * (frame["residents_15_24"] + frame["residents_25_44"]) / frame["population"]
    frame["one_person_household_pct"] = 100 * frame["one_person_households"] / frame["households"]
    frame = frame.loc[(frame["population"] >= 250) & (frame["housing_units"] >= 100)].copy()
    frame["supermarket_distance_imputed"] = frame["distance_large_supermarket_km"].isna()
    frame["distance_large_supermarket_km"] = frame["distance_large_supermarket_km"].fillna(frame["distance_large_supermarket_km"].median())
    frame["component_student_presence"] = robust_minmax(frame["student_age_share_pct"])
    frame["component_rental_access"] = robust_minmax(frame["rental_housing_pct"])
    frame["component_apartment_fit"] = robust_minmax(frame["apartment_housing_pct"])
    frame["component_single_household_fit"] = robust_minmax(frame["one_person_household_pct"])
    frame["component_cost_proxy"] = robust_minmax(frame["average_woz_eur_thousands"], invert=True)
    frame["component_grocery_access"] = robust_minmax(frame["distance_large_supermarket_km"], invert=True)
    for name, weights in PROFILES.items():
        frame[f"{name}_score"] = weighted_score(frame, weights).round(1)
    frame["balanced_rank"] = frame["balanced_score"].rank(method="min", ascending=False).astype(int)
    return frame.sort_values("balanced_rank").reset_index(drop=True)

def main() -> None:
    result = build_dataset()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)
    with sqlite3.connect(DATABASE) as connection:
        result.to_sql("neighbourhood_scores", connection, if_exists="replace", index=False)
    print(f"Wrote {len(result)} rows")

if __name__ == "__main__":
    main()
