# GridironCapIQ

Every NFL team works with roughly the same salary cap, yet results vary widely. This repo holds the raw data for exploring how winning teams spend that fixed budget differently from losing ones. What to build on it is still being decided.

## Data

Both files come from [nflverse](https://github.com/nflverse/nflverse-data) and were pulled on 2026-10-01.

| File | Rows | What it is |
|---|---|---|
| `data/raw/contracts.csv` | 53,041 | One row per player contract (OverTheCap data via nflverse) |
| `data/raw/games.csv` | 7,548 | One row per game, seasons 1999-2026 |

### contracts.csv

Converted from nflverse `historical_contracts.parquet` (release tag `contracts`). The older `historical_contracts.csv.gz` stopped updating in 2022, so use the parquet for fresh pulls. The nested `season_history` and `contract_history` columns were dropped in the conversion.

| Column | Meaning |
|---|---|
| `player`, `position` | Player name and position |
| `team` | Team nickname (e.g. "Chiefs"); players with several teams look like "NYJ/GB" |
| `is_active` | TRUE for current contracts |
| `year_signed`, `years` | Signing year and length. 1,106 rows have `year_signed` = 0 (missing) |
| `value`, `apy`, `guaranteed` | Total value, average per year, guaranteed money, in **$ millions** |
| `apy_cap_pct` | APY as a fraction of that year's cap (0.245 = 24.5%) |
| `inflated_*` | The money columns adjusted for cap growth |
| `otc_id`, `gsis_id`, `player_page` | OverTheCap id, nflverse player id, OverTheCap link |
| `height`, `weight`, `college`, `date_of_birth` | Player details |
| `draft_year`, `draft_round`, `draft_overall`, `draft_team` | Draft details |

### games.csv

From `https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv`.

| Column | Meaning |
|---|---|
| `game_id`, `season`, `week` | Game key, season, week |
| `game_type` | REG, WC, DIV, CON or SB |
| `home_team`, `away_team` | Team abbreviations (e.g. "KC"), including old codes OAK, SD, STL |
| `home_score`, `away_score` | Final scores (blank for games not played yet) |
| `result` | `home_score - away_score` |
| `spread_line`, `total_line`, moneylines | Betting lines |
| other columns | Rest days, roof, surface, weather, starting QBs, coaches, stadium |

Note that contracts use team nicknames while games use abbreviations, so joining them needs a mapping.

## Earlier version

The first version of this project (cleaning scripts, SQLite database, SQL analysis, Streamlit dashboard and write-up) is saved on the [`archive/pre-reset-2026-10-06`](https://github.com/floresandflores/GridironCapIQ/tree/archive/pre-reset-2026-10-06) branch.
