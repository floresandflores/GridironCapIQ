-- GridironCapIQ database schema (SQLite)
-- Money is in $ millions. Team IDs are current abbreviations (relocated teams use today's code).

PRAGMA foreign_keys = ON;

-- One row per franchise (32 rows)
CREATE TABLE teams (
    team_id     TEXT PRIMARY KEY,          -- e.g. 'KC'
    team_name   TEXT NOT NULL,             -- e.g. 'Kansas City Chiefs'
    nickname    TEXT NOT NULL,             -- e.g. 'Chiefs' (how the contracts data names teams)
    conference  TEXT NOT NULL,             -- 'AFC' or 'NFC'
    division    TEXT NOT NULL              -- e.g. 'AFC West'
);

-- One row per NFL season
CREATE TABLE seasons (
    season          INTEGER PRIMARY KEY,
    salary_cap      REAL,                  -- league-wide cap in $ millions (NULL if not recorded)
    games_per_team  INTEGER NOT NULL,      -- regular-season games each team plays
    is_complete     INTEGER NOT NULL       -- 1 once the regular season is finished
);

-- One row per game (regular season and playoffs)
CREATE TABLE games (
    game_id       TEXT PRIMARY KEY,        -- e.g. '2024_01_BAL_KC'
    season        INTEGER NOT NULL REFERENCES seasons(season),
    week          INTEGER NOT NULL,
    game_type     TEXT NOT NULL,           -- REG, WC, DIV, CON, SB
    home_team_id  TEXT NOT NULL REFERENCES teams(team_id),
    away_team_id  TEXT NOT NULL REFERENCES teams(team_id),
    home_score    INTEGER,                 -- NULL until the game is played
    away_score    INTEGER
);

-- One row per player
CREATE TABLE players (
    player_id       INTEGER PRIMARY KEY,   -- OverTheCap player ID
    gsis_id         TEXT,                  -- NFL's player ID, for joining other nflverse data
    name            TEXT NOT NULL,
    position        TEXT NOT NULL,         -- e.g. 'ED', 'LT'
    position_group  TEXT NOT NULL,         -- e.g. 'EDGE', 'OL'
    college         TEXT,
    draft_year      INTEGER,               -- NULL if undrafted
    draft_round     INTEGER,
    draft_overall   INTEGER
);

-- One row per contract signed
CREATE TABLE contracts (
    contract_id   INTEGER PRIMARY KEY,
    player_id     INTEGER NOT NULL REFERENCES players(player_id),
    team_id       TEXT REFERENCES teams(team_id),  -- NULL when the source lists several teams
    team_label    TEXT,                    -- team text exactly as the source has it, e.g. 'NYJ/GB'
    year_signed   INTEGER,                 -- NULL when the source has no year (it uses 0)
    years         INTEGER,
    value         REAL,                    -- total value
    apy           REAL,                    -- average per year
    guaranteed    REAL,
    apy_cap_pct   REAL,                    -- apy as a share of the cap in year_signed
    is_active     INTEGER NOT NULL         -- 1 if this is the player's current contract
);

-- One row per player per season per team: the real cap hit that season
CREATE TABLE player_seasons (
    player_id    INTEGER NOT NULL REFERENCES players(player_id),
    season       INTEGER NOT NULL REFERENCES seasons(season),
    team_id      TEXT NOT NULL REFERENCES teams(team_id),
    cap_number   REAL NOT NULL,            -- cap hit that season
    cap_percent  REAL,                     -- cap hit as a share of the cap, from OverTheCap
    cash_paid    REAL,
    PRIMARY KEY (player_id, season, team_id)
);

-- One row per team per finished season: the analysis table built by src/build_team_seasons.py
CREATE TABLE team_seasons (
    season          INTEGER NOT NULL REFERENCES seasons(season),
    team_id         TEXT NOT NULL REFERENCES teams(team_id),
    games           INTEGER NOT NULL,
    wins            INTEGER NOT NULL,
    ties            INTEGER NOT NULL,
    points_for      INTEGER NOT NULL,
    points_against  INTEGER NOT NULL,
    win_pct         REAL NOT NULL,
    cap_cb REAL, cap_edge REAL, cap_idl REAL, cap_lb REAL, cap_ol REAL, cap_qb REAL,
    cap_rb REAL, cap_s REAL, cap_st REAL, cap_te REAL, cap_wr REAL,
    cap_total       REAL NOT NULL,         -- sum of tracked cap hits (about 80% of the full cap)
    qb_cap_pct      REAL,                  -- cap_qb / cap_total
    PRIMARY KEY (season, team_id)
);

CREATE INDEX idx_games_season ON games(season);
CREATE INDEX idx_player_seasons_team ON player_seasons(team_id, season);
CREATE INDEX idx_contracts_player ON contracts(player_id);
