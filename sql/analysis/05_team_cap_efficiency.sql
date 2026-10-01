-- Q3: Which teams got the most wins out of their cap, 2013-2025?
-- Efficiency = average wins (per 17 games) for each 10 points of cap share spent.
-- Cap share = a team's tracked cap hits / the league salary cap. Since tracked cap covers
-- only ~80-89% of the real cap, the values compare teams with each other, not in absolute terms.

WITH team_totals AS (
    SELECT
        ts.team_id,
        COUNT(*)                                    AS seasons,
        AVG(ts.wins * 17.0 / ts.games)              AS avg_wins,
        AVG(100.0 * ts.cap_total / s.salary_cap)    AS avg_cap_share
    FROM team_seasons ts
    JOIN seasons s ON s.season = ts.season
    GROUP BY ts.team_id
)
SELECT
    RANK() OVER (ORDER BY avg_wins / (avg_cap_share / 10) DESC) AS efficiency_rank,
    t.team_name,
    ROUND(avg_wins, 1)                              AS avg_wins_per_17,
    ROUND(avg_cap_share, 1)                         AS avg_cap_share_pct,
    ROUND(avg_wins / (avg_cap_share / 10), 2)       AS wins_per_10pct_cap
FROM team_totals tt
JOIN teams t ON t.team_id = tt.team_id
ORDER BY efficiency_rank;
