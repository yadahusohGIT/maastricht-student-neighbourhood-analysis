# Methodology

## Unit of analysis

The unit of analysis is the CBS neighbourhood (`Buurt`) within the municipality of Maastricht.

Neighbourhoods are included only when they have at least 250 residents and 100 housing units. I added these thresholds because percentages from very small areas can be unstable, and some small Maastricht neighbourhoods are mainly industrial or non-residential.

## Variables

The model uses six indicators:

1. **Student-age presence**: residents aged 15–24 as a percentage of the population.
2. **Rental housing**: rental homes as a percentage of the housing stock.
3. **Apartment housing**: multi-family homes as a percentage of the housing stock.
4. **One-person households**: one-person households as a percentage of all households.
5. **WOZ value**: average WOZ value, reversed so lower values receive a higher score.
6. **Supermarket access**: average distance to a large supermarket, reversed so shorter distances receive a higher score.

These are neighbourhood characteristics. They are not direct measurements of student-room availability.

## Normalisation

Each indicator is converted to a 0–100 score.

Before min-max normalisation, values are clipped at the 5th and 95th percentiles. This reduces the effect of extreme neighbourhood values without deleting the neighbourhoods themselves.

For WOZ value and supermarket distance, the scale is reversed so that a higher component score always means a more favourable result.

## Missing data

Brusselsepoort has one missing supermarket-distance value in the source workbook. I replace it with the median distance among the eligible Maastricht neighbourhoods and keep a Boolean flag in the processed data.

I chose median imputation because it is simple, transparent, and has little influence on a six-factor score. A future version should investigate why the value is missing rather than relying on imputation.

## Profile weights

The profiles are preference scenarios, not statistically estimated models.

### Balanced

The balanced profile gives the most weight to student-age presence and rental housing. It is intended as a general comparison rather than an affordability model.

### Budget focused

The budget profile gives 40% of the score to the reversed WOZ proxy. This shows how the ranking changes when housing value matters more than living in a student-heavy area.

### Student hub

The student-hub profile gives 40% of the score to the 15–24 population share and 20% to one-person households.

### Housing availability

The housing-availability profile gives the most weight to rental and apartment housing. It does not measure actual vacancy; it only favours areas with housing-stock characteristics that may be more relevant to renters.

## Interpretation

The scores are relative to the eligible Maastricht neighbourhoods in this dataset. A score of 80 does not mean that a neighbourhood is objectively “80% suitable.”

The main analytical result is therefore not only the ranking. It is also how much the ranking changes under different assumptions.
