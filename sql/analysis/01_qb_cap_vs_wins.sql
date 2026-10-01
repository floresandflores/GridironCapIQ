-- Q1: Does spending a big share of the cap on quarterbacks go with winning?
-- Grain: one row per QB-spending band. Seasons 2013-2025, regular season wins.
-- QB share = all QB cap hits that season / the league salary cap.

WITH playoff_teams AS (
    -- A team made the playoffs if it played any non-regular-season game
    SELECT DISTINCT season, home_team_id AS team_id FROM games WHERE game_type <> 'REG'
    UNION
    SELECT DISTINCT season, away_team_id FROM games WHERE game_type <> 'REG'
),
team_qb AS (
    SELECT
        ts.season,
        ts.team_id,
        ts.wins,
        ts.games,
        ts.cap_qb / s.salary_cap AS qb_share,
        CASE WHEN pt.team_id IS NOT NULL THEN 1 ELSE 0 END AS made_playoffs
    FROM team_seasons ts
    JOIN seasons s ON s.season = ts.season
    LEFT JOIN playoff_teams pt ON pt.season = ts.season AND pt.team_id = ts.team_id
)
SELECT
    CASE
        WHEN qb_share < 0.05 THEN '1) under 5%'
        WHEN qb_share < 0.10 THEN '2) 5-10%'
        WHEN qb_share < 0.15 THEN '3) 10-15%'
        ELSE                      '4) 15% or more'
    END                                         AS qb_cap_band,
    COUNT(*)                                    AS team_seasons,
    ROUND(AVG(wins * 17.0 / games), 1)          AS avg_wins_per_17,
    ROUND(100.0 * AVG(made_playoffs), 0)        AS playoff_rate_pct
FROM team_qb
GROUP BY qb_cap_band
ORDER BY qb_cap_band;
