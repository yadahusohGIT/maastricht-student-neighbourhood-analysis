# Methodology

The unit of analysis is the CBS neighbourhood (`Buurt`) in Maastricht.

Neighbourhoods are ranked only when they have at least 250 residents and 100 housing units. This removes very small or largely non-residential areas.

Six inputs are winsorised at the 5th and 95th percentiles and converted to 0–100 scores. Average WOZ value and supermarket distance are reversed so a higher component score is favourable.

Brusselsepoort has one missing supermarket-distance value in the CBS workbook. It is retained by imputing Maastricht's median among eligible neighbourhoods and is flagged in the processed data.

The weighted score is a decision aid, not an objective measurement of the best place to live. Multiple profiles are included to expose preference sensitivity.
