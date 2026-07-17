# Maastricht Student Neighbourhood Suitability

An end-to-end Business Analytics portfolio project comparing Maastricht neighbourhoods from a student-housing perspective.

## Decision question

**Which Maastricht neighbourhoods combine student-age presence, rental availability, apartment stock, one-person households, a lower housing-value proxy and supermarket access?**

## What this demonstrates

- Current public-data sourcing and documentation
- Python data cleaning and feature engineering
- Transparent KPI and scoring design
- Preference and sensitivity analysis
- SQL and SQLite
- Data-quality validation
- Interactive HTML dashboard
- Stakeholder-facing limitations and recommendations

## Headline result

Under the balanced profile, the top five are **Binnenstad, Boschstraatkwartier, Randwyck, Statenkwartier and Sint Maartenspoort**.

Across the 38 ranked residential neighbourhoods, the median rental-housing share is **63.5%** and the median average WOZ proxy is approximately **€291k**.

These results do not establish that rooms are currently available.

## Dashboard

Open `dashboard/maastricht_student_neighbourhood_dashboard.html`. It supports four preference profiles:

- Balanced
- Budget focused
- Student hub
- Housing availability

## Data source

CBS, *Kerncijfers wijken en buurten 2025*.

- Dataset: https://www.cbs.nl/nl-nl/cijfers/detail/86165NED
- Workbook: https://download.cbs.nl/regionale-kaarten/kwb2025.xlsx
- Release used: 25 June 2026

## Balanced score

| Component | Weight |
|---|---:|
| Student-age presence | 25% |
| Rental access | 20% |
| Apartment fit | 15% |
| One-person-household fit | 15% |
| Lower-WOZ proxy | 15% |
| Grocery access | 10% |

Each input is winsorised at the 5th and 95th percentiles and normalised to 0–100. Neighbourhoods below 250 residents or 100 housing units are excluded.

Brusselsepoort has one missing supermarket-distance value. It is retained using the median among eligible Maastricht neighbourhoods and explicitly flagged.

## Critical limitations

1. WOZ value is not student rent.
2. The source does not contain live room listings, vacancy, room size or landlord rules.
3. Residents aged 15–24 are not identical to students.
4. Neighbourhood averages hide street-level variation.
5. The current version does not include cycling time to a faculty.
6. Score weights encode preferences and are not objective truths.

## Reproduce

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python src/download_data.py
python src/pipeline.py
python src/validate_data.py
```

The large CBS workbook and generated SQLite database are intentionally excluded from Git history. Run the download and pipeline scripts to reproduce them.

## Best extension

Collect a monthly sample of advertised student rooms and add rent, room size, furnished status, listing duration, neighbourhood and cycling time to SBE. This would replace the WOZ proxy with direct rental-market evidence.
