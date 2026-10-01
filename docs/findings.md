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

## Q2: Do teams that lean on cheap rookie contracts win more?

Queries: [`03_rookie_deals_vs_wins.sql`](../sql/analysis/03_rookie_deals_vs_wins.sql), [`04_early_picks_vs_wins.sql`](../sql/analysis/04_early_picks_vs_wins.sql)

A player counts as "on a rookie deal" when he was drafted and the season is within 3 years of his draft year (cap hits jump after year 3 in the data).

| Share of cap on rookie-deal players | Team-seasons | Avg wins (per 17) |
|---|---|---|
| under 22% | 68 | 9.1 |
| 22-27% | 161 | 8.7 |
| 27-32% | 104 | 8.7 |
| 32% or more | 83 | 7.3 |

| Premium picks (rounds 1-2) on rookie deals | Team-seasons | Avg wins (per 17) |
|---|---|---|
| 0-4 | 14 | 7.0 |
| 5-7 | 172 | 8.6 |
| 8-10 | 202 | 8.3 |
| 11 or more | 28 | 9.9 |

- Teams with a very high rookie share (32%+) win about 2 fewer games than teams under 22%. The overall correlation is -0.20.
- This probably does **not** mean rookies hurt. When a team has few expensive veterans, rookies take a bigger share of the cap by default, and teams without good veterans lose more. The share is partly a symptom.
- Premium picks tell a milder story: teams with 11 or more rounds 1-2 picks on rookie deals average 9.9 wins, but the correlation is only 0.05 and those groups are small.
- A fairer test (for Phase 4 later): compare rookie-deal players to veterans at the same position, and ask which group gives more wins per dollar.

## Caveats

- Correlation, not cause: good QBs get paid *because* they win.
- "Rookie deal" is inferred from draft year (first 4 seasons), not read from contract type.
- Cap hits cover about 79-89% of each team's cap (no dead money).
