"""Build the SQLite database from nflverse data.

Run from the project root:  python src/build_database.py
Output: data/gridironcapiq.db  (tables defined in sql/schema.sql)
"""
import sqlite3
from pathlib import Path

import nflreadpy as nfl
import pandas as pd

from build_team_seasons import (
    NICKNAME_TO_ABBR, OLD_ABBR_TO_CURRENT, POSITION_GROUPS, load_player_seasons,
)

DB_PATH = Path("data/gridironcapiq.db")
SCHEMA_PATH = Path("sql/schema.sql")
TEAM_SEASONS_CSV = Path("data/clean/team_seasons.csv")

# Official league salary cap per season, $ millions (NFL announcements, as listed on OverTheCap)
SALARY_CAP = {
    2011: 120.0, 2012: 120.6, 2013: 123.0, 2014: 133.0, 2015: 143.28, 2016: 155.27,
    2017: 167.0, 2018: 177.2, 2019: 188.2, 2020: 198.2, 2021: 182.5, 2022: 208.2,
    2023: 224.8, 2024: 255.4, 2025: 279.2,
}


def build_teams():
    teams = nfl.load_teams().to_pandas()
    # The source also lists old codes (OAK, SD, STL, LAR); keep the 32 current ones
    teams = teams[~teams["team_abbr"].isin(["OAK", "SD", "STL", "LAR"])]
    return teams.rename(columns={
        "team_abbr": "team_id", "team_nick": "nickname",
        "team_conf": "conference", "team_division": "division",
    })[["team_id", "team_name", "nickname", "conference", "division"]]


def build_games():
    games = nfl.load_schedules().to_pandas()
    games["home_team_id"] = games["home_team"].replace(OLD_ABBR_TO_CURRENT)
    games["away_team_id"] = games["away_team"].replace(OLD_ABBR_TO_CURRENT)
    return games[["game_id", "season", "week", "game_type", "home_team_id",
                  "away_team_id", "home_score", "away_score"]]


def build_seasons(games, player_seasons):
    regular = games[games["game_type"] == "REG"]
    per_team = pd.concat([
        regular[["season", "home_team_id", "home_score"]].set_axis(["season", "team", "score"], axis=1),
        regular[["season", "away_team_id", "away_score"]].set_axis(["season", "team", "score"], axis=1),
    ])
    scheduled = per_team.groupby(["season", "team"]).size().groupby("season").max()
    played = per_team.dropna(subset=["score"]).groupby(["season", "team"]).size().groupby("season").max()

    all_seasons = sorted(set(games["season"]) | set(player_seasons["season"]))
    seasons = pd.DataFrame({"season": all_seasons})
    seasons["salary_cap"] = seasons["season"].map(SALARY_CAP)
    seasons["games_per_team"] = seasons["season"].map(scheduled).fillna(0).astype(int)
    # Finished once the most-played team has played the full schedule (2022 had one cancelled game)
    seasons["is_complete"] = (
        seasons["season"].map(played).fillna(0) >= seasons["games_per_team"].where(lambda g: g > 0)
    ).astype(int)
    return seasons


def build_players_and_contracts():
    contracts = nfl.load_contracts().to_pandas()

    players = contracts.drop_duplicates("otc_id").rename(
        columns={"otc_id": "player_id", "player": "name"})
    players["position_group"] = players["position"].map(POSITION_GROUPS)
    players = players[["player_id", "gsis_id", "name", "position", "position_group",
                       "college", "draft_year", "draft_round", "draft_overall"]]

    contracts = contracts.rename(columns={"otc_id": "player_id", "team": "team_label"})
    contracts["team_id"] = contracts["team_label"].map(NICKNAME_TO_ABBR)
    contracts["year_signed"] = contracts["year_signed"].where(contracts["year_signed"] > 0)
    contracts["is_active"] = contracts["is_active"].astype(int)
    contracts.insert(0, "contract_id", range(1, len(contracts) + 1))
    contracts = contracts[["contract_id", "player_id", "team_id", "team_label", "year_signed",
                           "years", "value", "apy", "guaranteed", "apy_cap_pct", "is_active"]]
    return players, contracts


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.unlink(missing_ok=True)  # rebuild from scratch every run

    teams = build_teams()
    games = build_games()
    players, contracts = build_players_and_contracts()
    player_seasons = load_player_seasons().rename(columns={"otc_id": "player_id", "team": "team_id"})
    # Match the games data (1999 on); this also drops a stray season "0" row in the source.
    # Future seasons stay in as projections; seasons.is_complete marks them.
    player_seasons = player_seasons.loc[player_seasons["season"] >= 1999,
                                        ["player_id", "season", "team_id",
                                         "cap_number", "cap_percent", "cash_paid"]]
    seasons = build_seasons(games, player_seasons)

    if not TEAM_SEASONS_CSV.exists():
        raise SystemExit("Run python src/build_team_seasons.py first.")
    team_seasons = pd.read_csv(TEAM_SEASONS_CSV).rename(columns={"team": "team_id"})

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA_PATH.read_text())
        # Insert parents before children so every foreign key points at an existing row
        for name, df in [("teams", teams), ("seasons", seasons), ("games", games),
                         ("players", players), ("contracts", contracts),
                         ("player_seasons", player_seasons), ("team_seasons", team_seasons)]:
            df.to_sql(name, conn, if_exists="append", index=False)
            print(f"{name:15} {len(df):>7,} rows")

        problems = conn.execute("PRAGMA foreign_key_check").fetchall()
        print(f"\nforeign key problems: {len(problems)}")


if __name__ == "__main__":
    main()
