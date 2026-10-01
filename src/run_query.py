"""Run a .sql file against the database and print the result as a table.

Run from the project root:  python src/run_query.py sql/analysis/01_qb_cap_vs_wins.sql
"""
import sqlite3
import sys
from pathlib import Path

import pandas as pd

DB_PATH = Path("data/gridironcapiq.db")


def run(sql_path):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(Path(sql_path).read_text(), conn)


if __name__ == "__main__":
    print(run(sys.argv[1]).to_string(index=False))
