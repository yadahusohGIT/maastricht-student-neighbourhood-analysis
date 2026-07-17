"""Reusable scoring functions."""
from __future__ import annotations
import math
from typing import Mapping
import pandas as pd

PROFILES = {
    "balanced": {
        "component_student_presence": 0.25,
        "component_rental_access": 0.20,
        "component_apartment_fit": 0.15,
        "component_single_household_fit": 0.15,
        "component_cost_proxy": 0.15,
        "component_grocery_access": 0.10,
    },
    "budget_focused": {
        "component_student_presence": 0.10,
        "component_rental_access": 0.20,
        "component_apartment_fit": 0.10,
        "component_single_household_fit": 0.10,
        "component_cost_proxy": 0.40,
        "component_grocery_access": 0.10,
    },
    "student_hub": {
        "component_student_presence": 0.40,
        "component_rental_access": 0.20,
        "component_apartment_fit": 0.10,
        "component_single_household_fit": 0.20,
        "component_cost_proxy": 0.05,
        "component_grocery_access": 0.05,
    },
    "housing_availability": {
        "component_student_presence": 0.15,
        "component_rental_access": 0.35,
        "component_apartment_fit": 0.25,
        "component_single_household_fit": 0.10,
        "component_cost_proxy": 0.10,
        "component_grocery_access": 0.05,
    },
}

def robust_minmax(series: pd.Series, invert: bool = False) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").astype(float)
    low, high = values.quantile(0.05), values.quantile(0.95)
    if pd.isna(low) or pd.isna(high) or math.isclose(low, high):
        score = pd.Series(50.0, index=values.index)
    else:
        score = 100 * (values.clip(low, high) - low) / (high - low)
    return (100 - score if invert else score).clip(0, 100)

def weighted_score(frame: pd.DataFrame, weights: Mapping[str, float]) -> pd.Series:
    if not math.isclose(sum(weights.values()), 1.0, abs_tol=1e-9):
        raise ValueError("Weights must sum to 1")
    missing = sorted(set(weights) - set(frame.columns))
    if missing:
        raise KeyError(f"Missing components: {missing}")
    return sum(frame[column] * weight for column, weight in weights.items())
