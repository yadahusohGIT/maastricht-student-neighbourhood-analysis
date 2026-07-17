"""Scoring profiles used by the neighbourhood comparison."""

from __future__ import annotations

import math
from typing import Mapping

import pandas as pd


PROFILES: dict[str, dict[str, float]] = {
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


def robust_minmax(series: pd.Series, *, invert: bool = False) -> pd.Series:
    """Convert a numeric series to a 0-100 score.

    Values are clipped at the 5th and 95th percentiles before scaling so that
    a small number of extreme neighbourhoods do not dominate the range.
    """
    values = pd.to_numeric(series, errors="coerce").astype(float)
    lower = values.quantile(0.05)
    upper = values.quantile(0.95)

    if pd.isna(lower) or pd.isna(upper) or math.isclose(lower, upper):
        score = pd.Series(50.0, index=values.index)
    else:
        clipped = values.clip(lower, upper)
        score = 100 * (clipped - lower) / (upper - lower)

    if invert:
        score = 100 - score

    return score.clip(0, 100)


def weighted_score(
    frame: pd.DataFrame,
    weights: Mapping[str, float],
) -> pd.Series:
    """Calculate a weighted profile score after validating the weights."""
    if not math.isclose(sum(weights.values()), 1.0, abs_tol=1e-9):
        raise ValueError("Profile weights must sum to 1.0")

    missing_columns = sorted(set(weights) - set(frame.columns))
    if missing_columns:
        raise KeyError(f"Missing score components: {missing_columns}")

    return sum(frame[column] * weight for column, weight in weights.items())
