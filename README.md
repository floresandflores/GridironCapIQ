# GridironCapIQ

NFL Salary Cap Efficiency Analyzer. Every NFL team works with roughly the same salary cap, yet results vary widely. This project asks: **how do winning teams allocate a fixed budget differently from losing ones?**

It mirrors a common business problem: dividing a fixed budget across departments.

## Stack

- Data: [nflverse](https://github.com/nflverse) via `nflreadpy` (contracts sourced from OverTheCap.com)
- Python and pandas for cleaning
- SQLite for storage and SQL analysis
- Streamlit for the dashboard

## Progress

| Phase | Status |
|---|---|
| 1. Explore the data in Excel | In progress |
| 2. First Python: load, filter, clean | Done (`src/build_team_seasons.py`) |
| 3. SQLite database and ER diagram | In progress ([ER diagram](docs/er_diagram.md), `src/build_database.py`) |
| 4. SQL analysis | Not started |
| 5. Streamlit dashboard | Not started |
| 6. Business-case write-up | Not started |

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/load_data.py
```

This downloads the current contracts and schedules data and saves copies to `data/raw/` as CSV files (ignored by Git).

Then build the team-by-season table:

```bash
python src/build_team_seasons.py
```

Then build the database:

```bash
python src/build_database.py
```

This writes `data/gridironcapiq.db` (schema in `sql/schema.sql`, diagram in [docs/er_diagram.md](docs/er_diagram.md)).

The team-season step writes `data/clean/team_seasons.csv`: one row per team per season (2013-2025) with wins, points, and cap spending by position group. Cap numbers come from each player's real season-by-season cap hit (`season_history` in the contracts data). They cover the contracts OverTheCap tracks, roughly 80% of the full cap, so compare teams by share of tracked cap (for example `qb_cap_pct`), not by raw dollars.
