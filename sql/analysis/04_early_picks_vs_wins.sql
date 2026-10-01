-- Q2b: Same question, but only counting premium picks (rounds 1-2) still on rookie deals.
-- Late-round rookies are cheap but rarely change a season, so this isolates the picks teams
-- actually build around. Seasons 2013-2025.

WITH early_picks AS (
    SELECT ps.season, ps.team_id, COUNT(*) AS n, SUM(ps.cap_number) AS cap
    FROM player_seasons ps
    JOIN players p ON p.player_id = ps.player_id
    WHERE p.draft_round IN (1, 2)
      AND ps.season - p.draft_year BETWEEN 0 AND 3
    GROUP BY ps.season, ps.team_id
),
joined AS (
    SELECT
        ts.wins * 17.0 / ts.games       AS wins_17,
        COALESCE(ep.n, 0)               AS early_picks,
        COALESCE(ep.cap, 0) / ts.cap_total AS early_pct
    FROM team_seasons ts
    LEFT JOIN early_picks ep ON ep.season = ts.season AND ep.team_id = ts.team_id
)
SELECT
    CASE
        WHEN early_picks <= 4  THEN '1) 0-4 early picks'
        WHEN early_picks <= 7  THEN '2) 5-7'
        WHEN early_picks <= 10 THEN '3) 8-10'
        ELSE                        '4) 11 or more'
    END                              AS early_pick_band,
    COUNT(*)                         AS team_seasons,
    ROUND(AVG(100.0 * early_pct), 1) AS avg_cap_share_pct,
    ROUND(AVG(wins_17), 1)           AS avg_wins_per_17
FROM joined
GROUP BY early_pick_band
ORDER BY early_pick_band;
