-- Q1b: Which teams won the most while spending little on QBs?
-- Uses a window function to rank each team-season by wins within its QB-spending band.

WITH team_qb AS (
    SELECT
        ts.season,
        ts.team_id,
        ts.wins,
        ROUND(100.0 * ts.cap_qb / s.salary_cap, 1) AS qb_share_pct,
        CASE WHEN ts.cap_qb / s.salary_cap < 0.05 THEN 'under 5%' ELSE '5% or more' END AS band
    FROM team_seasons ts
    JOIN seasons s ON s.season = ts.season
),
ranked AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY band ORDER BY wins DESC) AS wins_rank_in_band
    FROM team_qb
)
SELECT season, team_id, wins, qb_share_pct
FROM ranked
WHERE band = 'under 5%' AND wins_rank_in_band <= 10
ORDER BY wins DESC, season;
