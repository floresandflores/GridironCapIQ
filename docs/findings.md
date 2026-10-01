# Findings

Running notes from Phase 4 (SQL analysis). Seasons 2013-2025, 416 team-seasons, regular-season wins scaled to a 17-game season. QB share = all QB cap hits for a team that season ÷ the league salary cap.

## Q1: Does a big QB cap share go with winning?

Query: [`sql/analysis/01_qb_cap_vs_wins.sql`](../sql/analysis/01_qb_cap_vs_wins.sql)

| QB share of cap | Team-seasons | Avg wins (per 17) | Made playoffs |
|---|---|---|---|
| under 5% | 105 | 8.1 | 37% |
| 5-10% | 131 | 8.1 | 37% |
| 10-15% | 120 | 9.1 | 46% |
| 15% or more | 60 | 8.8 | 42% |

- Paying a QB 10-15% of the cap goes with about one more win and a 9-point higher playoff rate than paying under 10%.
- Going past 15% doesn't buy more: wins and playoff rate dip slightly.
- Overall the link is weak (correlation 0.11 between QB share and wins), so QB spending alone explains very little.

## Q1b: Cheap QBs, big seasons

Query: [`sql/analysis/02_best_cheap_qb_seasons.sql`](../sql/analysis/02_best_cheap_qb_seasons.sql)

The best seasons from teams spending under 5% on QBs are mostly QBs on rookie contracts: 2019 BAL (14 wins, 2.2%), 2022 PHI (14, 2.7%), 2020 KC (14, 3.7%), 2025 DEN (14, 3.4%), 2025 NE (14, 4.5%), 2013 SEA (13, 1.3%).

This points at the brief's rookie-contract question: a good QB on a rookie deal frees cap for the rest of the roster. That's the next query.

## Caveats

- Correlation, not cause: good QBs get paid *because* they win.
- Cap hits cover about 79-89% of each team's cap (no dead money).
