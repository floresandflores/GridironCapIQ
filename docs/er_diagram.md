# Database design (ER diagram)

The database lives at `data/gridironcapiq.db` and is built by `python src/build_database.py` from the tables in [`sql/schema.sql`](../sql/schema.sql). Money is in $ millions.

```mermaid
erDiagram
    teams ||--o{ games : "plays at home"
    teams ||--o{ games : "plays away"
    seasons ||--o{ games : contains
    players ||--o{ contracts : signs
    teams |o--o{ contracts : "signed with"
    players ||--o{ player_seasons : "has a cap hit in"
    teams ||--o{ player_seasons : "pays"
    seasons ||--o{ player_seasons : "falls in"
    teams ||--o{ team_seasons : "has a record in"
    seasons ||--o{ team_seasons : "has"

    teams {
        TEXT team_id PK
        TEXT team_name
        TEXT nickname
        TEXT conference
        TEXT division
    }
    seasons {
        INTEGER season PK
        REAL salary_cap
        INTEGER games_per_team
        INTEGER is_complete
    }
    games {
        TEXT game_id PK
        INTEGER season FK
        INTEGER week
        TEXT game_type
        TEXT home_team_id FK
        TEXT away_team_id FK
        INTEGER home_score
        INTEGER away_score
    }
    players {
        INTEGER player_id PK
        TEXT gsis_id
        TEXT name
        TEXT position
        TEXT position_group
        INTEGER draft_year
        INTEGER draft_round
        INTEGER draft_overall
    }
    contracts {
        INTEGER contract_id PK
        INTEGER player_id FK
        TEXT team_id FK
        INTEGER year_signed
        INTEGER years
        REAL value
        REAL apy
        REAL guaranteed
        REAL apy_cap_pct
        INTEGER is_active
    }
    player_seasons {
        INTEGER player_id PK,FK
        INTEGER season PK,FK
        TEXT team_id PK,FK
        REAL cap_number
        REAL cap_percent
        REAL cash_paid
    }
    team_seasons {
        INTEGER season PK,FK
        TEXT team_id PK,FK
        INTEGER wins
        REAL win_pct
        REAL cap_qb
        REAL cap_total
        REAL qb_cap_pct
    }
```

## How to read it

- **One table per real-world thing.** Teams, seasons, games, players and contracts each get their own table, so a fact like a team's division is stored once.
- **`player_seasons` is the bridge to money.** A contract is signed once, but a player counts against the cap every season. This table holds the real cap hit per player, per season, per team, and it's what cap-by-position totals are built from.
- **`team_seasons` is the analysis table.** One row per team per finished season, with wins and cap spending by position group. In Phase 4 the goal is to rebuild it with SQL from `games` and `player_seasons`.
- **Composite primary keys.** `player_seasons` is unique on (player, season, team) because a player traded mid-season has a cap hit with two teams.
- **`contracts.team_id` can be empty** when the source lists several teams (like `NYJ/GB`); the original text is kept in `team_label`.

## Known limits

- Cap hits cover the contracts OverTheCap tracks: about 80-89% of the league cap per team. Compare teams by share, not raw dollars.
- Dead money (cap charges for players no longer on the team) is not in the data.
- `seasons.salary_cap` is filled for 2011-2025; later seasons are NULL.
