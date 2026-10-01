"""Build the team-by-season table: wins plus cap spending by position group.

Run from the project root:  python src/build_team_seasons.py
Output: data/clean/team_seasons.csv  (one row per team per season)
"""
from pathlib import Path

import nflreadpy as nfl
import pandas as pd

CLEAN_DIR = Path("data/clean")
FIRST_SEASON = 2013  # earlier seasons have too few contracts recorded to be reliable

# Contracts name teams by nickname; games use abbreviations.
# Relocated teams are mapped to their current abbreviation so each franchise is one team.
NICKNAME_TO_ABBR = {
    "49ers": "SF", "Bears": "CHI", "Bengals": "CIN", "Bills": "BUF", "Broncos": "DEN",
    "Browns": "CLE", "Buccaneers": "TB", "Cardinals": "ARI", "Chargers": "LAC",
    "Chiefs": "KC", "Colts": "IND", "Commanders": "WAS", "Cowboys": "DAL",
    "Dolphins": "MIA", "Eagles": "PHI", "Falcons": "ATL", "Giants": "NYG",
    "Jaguars": "JAX", "Jets": "NYJ", "Lions": "DET", "Packers": "GB",
    "Panthers": "CAR", "Patriots": "NE", "Raiders": "LV", "Rams": "LA",
    "Ravens": "BAL", "Redskins": "WAS", "Saints": "NO", "Seahawks": "SEA",
    "Steelers": "PIT", "Texans": "HOU", "Titans": "TEN", "Vikings": "MIN",
    "Washington": "WAS",
}
OLD_ABBR_TO_CURRENT = {"OAK": "LV", "SD": "LAC", "STL": "LA"}

POSITION_GROUPS = {
    "QB": "QB", "RB": "RB", "FB": "RB", "WR": "WR", "TE": "TE",
    "LT": "OL", "LG": "OL", "C": "OL", "RG": "OL", "RT": "OL",
    "ED": "EDGE", "IDL": "IDL", "LB": "LB", "CB": "CB", "S": "S",
    "K": "ST", "P": "ST", "LS": "ST",
}


def load_player_seasons():
    """Flatten each player's season-by-season cap history into one row per player-season-team."""
    contracts = nfl.load_contracts().to_pandas()
    # season_history covers a player's whole career, so keep one row per player
    contracts = contracts.drop_duplicates("otc_id")

    rows = []
    for otc_id, position, history in zip(
        contracts["otc_id"], contracts["position"], contracts["season_history"]
    ):
        if history is None:
            continue
        for year in history:
            if not str(year.get("year")).isdigit():  # skips the "Total" row
                continue
            rows.append((otc_id, int(year["year"]), year["team"], position,
                         year["cap_number"], year["cap_percent"], year["cash_paid"]))
    seasons = pd.DataFrame(rows, columns=["otc_id", "season", "team_name", "position",
                                          "cap_number", "cap_percent", "cash_paid"])

    seasons["team"] = seasons["team_name"].map(NICKNAME_TO_ABBR)
    seasons["position_group"] = seasons["position"].map(POSITION_GROUPS)
    return seasons.dropna(subset=["team", "position_group", "cap_number"])


def build_cap_by_position():
    """Total cap spending per team per season, split by position group."""
    cap = load_player_seasons()

    by_position = cap.pivot_table(
        index=["season", "team"], columns="position_group",
        values="cap_number", aggfunc="sum", fill_value=0,
    )
    by_position.columns = [f"cap_{col.lower()}" for col in by_position.columns]
    return by_position.reset_index()


def build_results():
    """Turn one-row-per-game into one row per team per season (regular season only)."""
    games = nfl.load_schedules().to_pandas()
    games = games[(games["game_type"] == "REG") & games["home_score"].notna()].copy()
    for col in ("home_team", "away_team"):
        games[col] = games[col].replace(OLD_ABBR_TO_CURRENT)

    home = pd.DataFrame({
        "season": games["season"], "team": games["home_team"],
        "points_for": games["home_score"], "points_against": games["away_score"],
    })
    away = pd.DataFrame({
        "season": games["season"], "team": games["away_team"],
        "points_for": games["away_score"], "points_against": games["home_score"],
    })
    team_games = pd.concat([home, away], ignore_index=True)
    team_games["win"] = (team_games["points_for"] > team_games["points_against"]).astype(int)
    team_games["tie"] = (team_games["points_for"] == team_games["points_against"]).astype(int)

    results = team_games.groupby(["season", "team"], as_index=False).agg(
        games=("win", "size"), wins=("win", "sum"), ties=("tie", "sum"),
        points_for=("points_for", "sum"), points_against=("points_against", "sum"),
    )
    results["win_pct"] = (results["wins"] + 0.5 * results["ties"]) / results["games"]
    return results


def main():
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    table = build_results().merge(build_cap_by_position(), on=["season", "team"], how="left")

    # Keep only finished seasons from FIRST_SEASON on. A season is finished once teams have
    # played a full schedule (16 games before 2021, 17 after). One game can be missing
    # (the 2022 Bills-Bengals game was cancelled), so allow games to be one short of the max.
    season_games = table.groupby("season")["games"].transform("max")
    table = table[(table["season"] >= FIRST_SEASON) & (season_games >= 16) & (table["games"] >= season_games - 1)]

    cap_cols = [c for c in table.columns if c.startswith("cap_")]
    table = table.assign(cap_total=table[cap_cols].sum(axis=1))
    table["qb_cap_pct"] = table["cap_qb"] / table["cap_total"]

    table.to_csv(CLEAN_DIR / "team_seasons.csv", index=False)

    print(f"{len(table)} team-seasons, {table['season'].min()} to {table['season'].max()}")
    print(f"teams per season: {sorted(table.groupby('season')['team'].nunique().unique())}")
    print(f"missing cap data: {int(table['cap_total'].eq(0).sum())} rows")
    print("\nTop 5 by QB share of tracked cap:")
    print(table.nlargest(5, "qb_cap_pct")[["season", "team", "wins", "qb_cap_pct"]].to_string(index=False))


if __name__ == "__main__":
    main()
