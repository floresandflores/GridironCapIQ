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

## Q3: Which teams got the most wins out of their cap?

Query: [`05_team_cap_efficiency.sql`](../sql/analysis/05_team_cap_efficiency.sql)

Efficiency here is average wins (per 17 games) per 10 points of cap share spent, 2013-2025.

| Rank | Team | Avg wins | Avg cap share |
|---|---|---|---|
| 1 | Kansas City Chiefs | 11.9 | 90.6% |
| 2 | Seattle Seahawks | 10.9 | 85.5% |
| 3 | New England Patriots | 10.7 | 85.9% |
| 4 | Philadelphia Eagles | 10.2 | 82.8% |
| 5 | Buffalo Bills | 10.2 | 85.1% |
| ... | | | |
| 28 | Washington Commanders | 6.7 | 86.7% |
| 30 | Cleveland Browns | 5.8 | 82.9% |
| 31 | Jacksonville Jaguars | 5.9 | 85.0% |
| 32 | New York Jets | 5.7 | 82.2% |

- The top and bottom of the table are the same teams that win and lose the most, because cap share varies only from about 80% to 95% across teams. Almost all of the ranking comes from wins.
- Cap share differences are partly a data artifact (how many contracts are tracked per team), so this ranking says less about "who spends smartly" than a true cap-efficiency measure would. A better version needs dead money and full-roster cap totals.

## Q4: Which positions show the biggest gap between big spenders and low spenders?

Query: [`06_position_spend_vs_wins.sql`](../sql/analysis/06_position_spend_vs_wins.sql)

Each team-season is placed in the top, middle or bottom third of spending on a position group (as a share of the league cap). Gap = average wins of the top third minus the bottom third.

| Position group | Top-third wins | Bottom-third wins | Gap |
|---|---|---|---|
| Safety | 9.0 | 8.1 | +0.86 |
| Edge rusher | 8.9 | 8.2 | +0.73 |
| Tight end | 8.8 | 8.1 | +0.72 |
| Quarterback | 8.9 | 8.2 | +0.67 |
| Offensive line | 8.8 | 8.3 | +0.46 |
| Wide receiver | 8.5 | 8.2 | +0.30 |
| Linebacker | 8.8 | 8.6 | +0.26 |
| Cornerback | 8.5 | 8.4 | +0.13 |
| Interior D-line | 8.4 | 8.3 | +0.10 |
| Running back | 8.5 | 8.5 | -0.01 |

- Running back is the clearest case of spending that doesn't show up in wins: teams paying RBs a lot win no more than teams paying them little.
- Gaps are small (under one win), so treat the ordering as a hint. Safety, edge and tight end lead, but these gaps could partly be noise.
- Same caveat as before: correlation, not cause.

## Caveats

- Correlation, not cause: good QBs get paid *because* they win.
- "Rookie deal" is inferred from draft year (first 4 seasons), not read from contract type.
- Cap hits cover about 79-89% of each team's cap (no dead money).
