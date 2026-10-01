"""Download the current contracts and schedules data and save raw CSV copies.

Run from the project root:  python src/load_data.py
"""
from pathlib import Path

import nflreadpy as nfl

RAW_DIR = Path("data/raw")


def load_contracts():
    """One row per player contract. Money columns are in $ millions."""
    # nflreadpy returns a polars table; .to_pandas() converts it to a pandas DataFrame
    contracts = nfl.load_contracts().to_pandas()
    # These two columns hold nested lists, which CSV files can't store
    return contracts.drop(columns=["season_history", "contract_history"])


def load_games():
    """One row per game (the schedule plus results). result = home_score - away_score."""
    return nfl.load_schedules().to_pandas()


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    contracts = load_contracts()
    games = load_games()

    contracts.to_csv(RAW_DIR / "contracts.csv", index=False)
    games.to_csv(RAW_DIR / "games.csv", index=False)

    print(f"contracts: {contracts.shape[0]:,} rows x {contracts.shape[1]} columns")
    print(f"games:     {games.shape[0]:,} rows x {games.shape[1]} columns")
    print(f"active contracts: {int(contracts['is_active'].sum()):,}")
    print(f"seasons covered:  {games['season'].min()} to {games['season'].max()}")


if __name__ == "__main__":
    main()
