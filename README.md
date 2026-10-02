# GridironCapIQ

**How do winning NFL teams divide a fixed salary cap differently from losing ones?**

An analysis of 13 seasons of NFL contract and game data (2013-2025): a Python data pipeline, a SQLite database, SQL analysis, and an interactive Streamlit dashboard.

## The business problem

Every NFL team plays under roughly the same salary cap, yet results vary widely: some teams win 13 games a year and others win 4. Dividing a fixed budget across competing priorities is a problem every organization has, whether it is a department budget or a hiring plan. The cap makes it unusually measurable, because every dollar is public and every outcome is a win or a loss.

This project asks which allocation choices go with winning, and which spending shows no return.

## Key findings

All results are regular seasons from 2013 to 2025 (416 team-seasons), with wins scaled to a 17-game season. Full tables and the SQL behind them are in [docs/findings.md](docs/findings.md).

**1. A mid-sized quarterback investment goes with winning. Going bigger does not help.**
Teams that put 10-15% of the cap on quarterbacks averaged 9.1 wins and made the playoffs 46% of the time, against 8.1 wins and 37% for teams under 10%. Teams past 15% did slightly worse than the 10-15% group (8.8 wins). Across all teams the link is weak (correlation 0.11), so QB spending explains very little on its own.

**2. Running back spending shows no link to wins.**
Comparing the top and bottom third of spenders at each position, teams that spend a lot on running backs win no more than teams that spend little (gap of -0.01 wins). Safety (+0.86), edge rusher (+0.73), tight end (+0.72) and quarterback (+0.67) show the largest gaps, though every gap is under one win.

**3. Rookie-heavy rosters win less, probably as a symptom and not a cause.**
Teams that put 32% or more of their tracked cap on players in their first four seasons averaged 7.3 wins, against 9.1 for teams under 22%. That share is partly mechanical: a team with few expensive veterans has a larger rookie share by default, and those teams tend to be weaker. Counting only round 1-2 picks, the link nearly disappears (correlation 0.05).

**4. Some of the best low-QB-cost seasons came from young quarterbacks.**
2019 Baltimore, 2022 Philadelphia and 2025 Denver each won 14 games while spending under 4% of the cap at quarterback.

## What I would do with this

If this were a real front-office question, I would treat these as places to look, not conclusions:

- **Do not pay quarterbacks past about 15% of the cap on the strength of wins alone.** The data shows no extra return beyond that point.
- **Question large running back contracts.** This is the clearest case of spending that does not show up in wins.
- **Test safety, edge rusher and tight end more closely.** They show the largest gaps, but the gaps are small. The next step is to compare players at the same position, not whole rosters.
- **Compare rookie-deal players with veterans at the same position,** in wins per dollar, before drawing any conclusion about building through the draft.

## Limits of the analysis

Being clear about these is part of the work:

- **Correlation, not cause.** Good players get paid because they win, so spending and winning are tangled together.
- **The data covers about 79-89% of each team's cap.** It is built from each player's real season-by-season cap hit, but it misses some contracts and all dead money (charges for players a team already cut). Teams are compared by share of cap, not raw dollars.
- **The team efficiency ranking is mostly a ranking by wins,** because the tracked share of cap varies little between teams.
- **"Rookie deal" is inferred** from draft year (first four seasons), not read from the contract type.
- Differences between groups are often under one win per season, so many are within normal year-to-year noise.

## How it works

```
nflverse data  ->  Python (pandas)  ->  SQLite  ->  SQL analysis  ->  Streamlit dashboard
 (via nflreadpy)    clean + reshape      7 linked       6 queries       key findings, team
 contracts, games                         tables                         explorer, rankings
```

1. **Load and reshape (Python).** `src/build_team_seasons.py` pulls contract and schedule data with `nflreadpy`, flattens each player's career cap history into one row per player-season, maps contract team nicknames to game abbreviations (handling relocated franchises), and builds one row per team per season with wins and cap spending by position group.
2. **Store (SQLite).** `src/build_database.py` loads seven tables with primary and foreign keys: teams, seasons, games, players, contracts, player_seasons and team_seasons. See the [ER diagram](docs/er_diagram.md) and [`sql/schema.sql`](sql/schema.sql).
3. **Analyze (SQL).** Six queries in [`sql/analysis/`](sql/analysis/) use CTEs, joins, conditional aggregation and window functions (`RANK`, `NTILE`).
4. **Present (Streamlit).** `streamlit_app.py` opens with the key findings, then lets you pick a season and team to see cap by position against the league average, a QB spending vs wins scatter plot, and team rankings. The headline numbers come from the same SQL files as the analysis.
5. **Stay current.** A scheduled GitHub Action ([`refresh-data.yml`](.github/workflows/refresh-data.yml)) rebuilds the database from the latest nflverse data every Tuesday, runs sanity checks ([`src/check_database.py`](src/check_database.py)), and commits only if the data changed. If anything looks wrong, it stops before committing.

## Run it yourself

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python src/build_team_seasons.py   # builds data/clean/team_seasons.csv
python src/build_database.py       # builds data/gridironcapiq.db
streamlit run streamlit_app.py     # opens the dashboard
```

Run any analysis query on its own:

```bash
python src/run_query.py sql/analysis/01_qb_cap_vs_wins.sql
```

## Project layout

```
streamlit_app.py            the dashboard
src/                        data pipeline (build_team_seasons, build_database, check_database, run_query, load_data)
sql/schema.sql              database schema
sql/analysis/               the six analysis queries
docs/findings.md            full results tables and caveats
docs/er_diagram.md          database design and ER diagram
data/gridironcapiq.db       the built database (kept in the repo so the hosted app can read it)
.github/workflows/          scheduled data refresh
```

## Data

[nflverse](https://github.com/nflverse) (free, open-source NFL data). Contract data is sourced from OverTheCap.com, which I used to sanity-check numbers.

Built with Python, pandas, SQLite, SQL and Streamlit.
