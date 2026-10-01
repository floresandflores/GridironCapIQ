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
| 2. First Python: load, filter, clean | Started (`src/load_data.py`) |
| 3. SQLite database and ER diagram | Not started |
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
