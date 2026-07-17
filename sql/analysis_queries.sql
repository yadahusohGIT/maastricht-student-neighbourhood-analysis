-- 1. Top ten neighbourhoods under the balanced profile.
SELECT
    balanced_rank,
    neighbourhood,
    balanced_score,
    student_age_share_pct,
    rental_housing_pct,
    average_woz_eur_thousands
FROM neighbourhood_scores
ORDER BY balanced_rank
LIMIT 10;


-- 2. Areas with high rental housing and a below-average WOZ proxy.
WITH city_average AS (
    SELECT AVG(average_woz_eur_thousands) AS average_woz
    FROM neighbourhood_scores
)
SELECT
    neighbourhood,
    rental_housing_pct,
    average_woz_eur_thousands,
    balanced_score
FROM neighbourhood_scores
CROSS JOIN city_average
WHERE rental_housing_pct >= 60
  AND average_woz_eur_thousands < average_woz
ORDER BY rental_housing_pct DESC;


-- 3. Neighbourhoods whose position changes most between profiles.
SELECT
    neighbourhood,
    balanced_rank,
    budget_focused_rank,
    student_hub_rank,
    housing_availability_rank,
    MAX(
        balanced_rank,
        budget_focused_rank,
        student_hub_rank,
        housing_availability_rank
    )
    -
    MIN(
        balanced_rank,
        budget_focused_rank,
        student_hub_rank,
        housing_availability_rank
    ) AS rank_range
FROM neighbourhood_scores
ORDER BY rank_range DESC
LIMIT 10;


-- 4. Check the rows where supermarket distance was imputed.
SELECT
    neighbourhood,
    distance_large_supermarket_km,
    supermarket_distance_imputed
FROM neighbourhood_scores
WHERE supermarket_distance_imputed = 1;
