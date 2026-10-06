"""Export clean CSVs from the database for the Power BI version of the dashboard.

Power BI can't open SQLite files, so this writes one CSV per table into data/powerbi/.
The tables form a star schema: two fact tables (team_seasons, position_cap) joined to
three lookup tables (teams, seasons, positions), plus three small findings tables.

Run from the project root:  python src/export_powerbi.py
Percentages are stored as fractions (0.12 = 12%) so Power BI can format them as %.
"""
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("data/gridironcapiq.db")
OUT_DIR = Path("data/powerbi")
SQL_DIR = Path("sql/analysis")

# Position groups in display order, with the team_seasons column that holds each one
POSITIONS = {
    "QB": "cap_qb", "RB": "cap_rb", "WR": "cap_wr", "TE": "cap_te", "OL": "cap_ol",
    "EDGE": "cap_edge", "IDL": "cap_idl", "LB": "cap_lb", "CB": "cap_cb", "S": "cap_s",
    "Special teams": "cap_st",
}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        teams = pd.read_sql("SELECT team_id, team_name, nickname, conference, division FROM teams", conn)
        ts = pd.read_sql("SELECT * FROM team_seasons", conn)
        seasons = pd.read_sql("SELECT season, salary_cap, games_per_team FROM seasons", conn)
        playoffs = pd.read_sql("""
            SELECT DISTINCT season, home_team_id AS team_id FROM games WHERE game_type <> 'REG'
            UNION
            SELECT DISTINCT season, away_team_id FROM games WHERE game_type <> 'REG'
        """, conn)
        findings = {name: pd.read_sql((SQL_DIR / f).read_text(), conn) for name, f in [
            ("findings_qb_bands", "01_qb_cap_vs_wins.sql"),
            ("findings_rookie_bands", "03_rookie_deals_vs_wins.sql"),
            ("findings_position_gaps", "06_position_spend_vs_wins.sql"),
        ]}

    # Only the seasons the analysis covers (finished seasons from 2013 on)
    seasons = seasons[seasons["season"].isin(ts["season"].unique())].rename(
        columns={"salary_cap": "salary_cap_m"})
    ts = ts.merge(seasons[["season", "salary_cap_m"]], on="season")

    # ---- fact table 1: one row per team per season
    playoffs["made_playoffs"] = 1
    ts = ts.merge(playoffs, on=["season", "team_id"], how="left")
    team_seasons = pd.DataFrame({
        "season": ts["season"],
        "team_id": ts["team_id"],
        "games": ts["games"],
        "wins": ts["wins"],
        "losses": ts["games"] - ts["wins"] - ts["ties"],
        "ties": ts["ties"],
        "wins_per_17": (ts["wins"] * 17 / ts["games"]).round(2),
        "win_pct": ts["win_pct"].round(3),
        "points_for": ts["points_for"],
        "points_against": ts["points_against"],
        "made_playoffs": ts["made_playoffs"].fillna(0).astype(int),
        "tracked_cap_m": ts["cap_total"].round(3),
        "tracked_cap_share": (ts["cap_total"] / ts["salary_cap_m"]).round(4),
        "qb_cap_m": ts["cap_qb"].round(3),
        "qb_share_of_tracked": ts["qb_cap_pct"].round(4),
        "qb_share_of_league_cap": (ts["cap_qb"] / ts["salary_cap_m"]).round(4),
    })

    # ---- fact table 2: one row per team per season per position group ("long" shape)
    long = ts.melt(id_vars=["season", "team_id", "cap_total"], value_vars=list(POSITIONS.values()),
                   var_name="column", value_name="cap_m")
    long["position"] = long["column"].map({col: pos for pos, col in POSITIONS.items()})
    long["cap_m"] = long["cap_m"].fillna(0)
    long["share_of_tracked"] = long["cap_m"] / long["cap_total"]
    # League average share for that position and season, so the browser version can chart it
    # without DAX (Power BI Desktop users build this as a measure instead)
    long["league_avg_share"] = long.groupby(["season", "position"])["share_of_tracked"].transform("mean")
    position_cap = long[["season", "team_id", "position", "cap_m", "share_of_tracked", "league_avg_share"]].round(4)

    positions = pd.DataFrame({"position": list(POSITIONS), "sort_order": range(1, len(POSITIONS) + 1)})

    tables = {
        "teams": teams,
        "seasons": seasons,
        "positions": positions,
        "team_seasons": team_seasons.sort_values(["season", "team_id"]),
        "position_cap": position_cap.sort_values(["season", "team_id", "position"]),
        **findings,
    }
    for name, df in tables.items():
        df.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: {len(df)} rows")


if __name__ == "__main__":
    main()
