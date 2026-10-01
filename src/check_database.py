"""Sanity-check the rebuilt database before it is committed.

Run from the project root:  python src/check_database.py
Exits with an error (so an automated refresh stops) if anything looks wrong.
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/gridironcapiq.db")


def main():
    problems = []
    with sqlite3.connect(DB_PATH) as conn:
        def one(sql):
            return conn.execute(sql).fetchone()[0]

        if one("SELECT COUNT(*) FROM teams") != 32:
            problems.append("teams should have 32 rows")
        if one("SELECT COUNT(*) FROM games") < 7000:
            problems.append("games has fewer rows than expected")
        if one("SELECT COUNT(*) FROM player_seasons") < 40000:
            problems.append("player_seasons has fewer rows than expected")

        # Every finished season from 2013 on should have all 32 teams, once each
        bad_seasons = conn.execute(
            "SELECT season, COUNT(*) FROM team_seasons GROUP BY season HAVING COUNT(*) <> 32"
        ).fetchall()
        if bad_seasons:
            problems.append(f"seasons without 32 teams: {bad_seasons}")
        if one("SELECT MIN(season) FROM team_seasons") != 2013:
            problems.append("team_seasons should start in 2013")

        # Tracked cap should be a believable share of the league cap
        low = conn.execute(
            """SELECT ts.season, ts.team_id FROM team_seasons ts JOIN seasons s USING (season)
               WHERE s.salary_cap IS NOT NULL AND ts.cap_total / s.salary_cap NOT BETWEEN 0.5 AND 1.1"""
        ).fetchall()
        if low:
            problems.append(f"{len(low)} team-seasons with tracked cap outside 50-110% of the cap")

        if conn.execute("PRAGMA foreign_key_check").fetchall():
            problems.append("foreign key problems")

        newest = one("SELECT MAX(season) FROM team_seasons")

    if problems:
        print("CHECK FAILED:")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print(f"database OK (latest finished season: {newest})")


if __name__ == "__main__":
    main()
