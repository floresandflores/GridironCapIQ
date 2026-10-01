-- Q2: Do teams that lean on cheap rookie contracts win more?
-- A player counts as "on a rookie deal" when he was drafted and this season is within
-- 3 seasons of his draft year (the first 4 seasons). Cap hits jump after year 3 in the data.
-- Two measures per team-season:
--   rookie_pct  = share of the team's tracked cap going to rookie-deal players
--   rookie_core = how many drafted players on rookie deals the team carries
-- Bands are set around the typical team (median 26%), since every roster carries many cheap rookies.
-- Seasons 2013-2025.

WITH team_rookies AS (
    SELECT
        ps.season,
        ps.team_id,
        SUM(ps.cap_number)  AS rookie_cap,
        COUNT(*)            AS rookie_count
    FROM player_seasons ps
    JOIN players p ON p.player_id = ps.player_id
    WHERE p.draft_year IS NOT NULL
      AND ps.season - p.draft_year BETWEEN 0 AND 3
    GROUP BY ps.season, ps.team_id
),
joined AS (
    SELECT
        ts.season,
        ts.team_id,
        ts.wins * 17.0 / ts.games                 AS wins_17,
        COALESCE(tr.rookie_cap, 0) / ts.cap_total AS rookie_pct,
        COALESCE(tr.rookie_count, 0)              AS rookie_count
    FROM team_seasons ts
    LEFT JOIN team_rookies tr ON tr.season = ts.season AND tr.team_id = ts.team_id
)
SELECT
    CASE
        WHEN rookie_pct < 0.22 THEN '1) under 22%'
        WHEN rookie_pct < 0.27 THEN '2) 22-27%'
        WHEN rookie_pct < 0.32 THEN '3) 27-32%'
        ELSE                        '4) 32% or more'
    END                             AS rookie_cap_band,
    COUNT(*)                        AS team_seasons,
    ROUND(AVG(rookie_count), 1)     AS avg_rookie_players,
    ROUND(AVG(wins_17), 1)          AS avg_wins_per_17
FROM joined
GROUP BY rookie_cap_band
ORDER BY rookie_cap_band;
