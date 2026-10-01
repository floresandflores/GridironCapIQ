-- Q4: Which positions show the biggest gap in wins between teams that spend a lot
-- and teams that spend little?
-- For each position group, every team-season is placed in the top, middle or bottom third
-- of spending (NTILE) among all team-seasons, then average wins are compared.
-- Spending is measured as share of the league cap. Seasons 2013-2025.

WITH spend AS (
    SELECT ts.season, ts.team_id, ts.wins * 17.0 / ts.games AS wins_17, s.salary_cap, 'QB'   AS pos, ts.cap_qb   AS cap FROM team_seasons ts JOIN seasons s USING (season)
    UNION ALL SELECT ts.season, ts.team_id, ts.wins * 17.0 / ts.games, s.salary_cap, 'RB',   ts.cap_rb   FROM team_seasons ts JOIN seasons s USING (season)
    UNION ALL SELECT ts.season, ts.team_id, ts.wins * 17.0 / ts.games, s.salary_cap, 'WR',   ts.cap_wr   FROM team_seasons ts JOIN seasons s USING (season)
    UNION ALL SELECT ts.season, ts.team_id, ts.wins * 17.0 / ts.games, s.salary_cap, 'TE',   ts.cap_te   FROM team_seasons ts JOIN seasons s USING (season)
    UNION ALL SELECT ts.season, ts.team_id, ts.wins * 17.0 / ts.games, s.salary_cap, 'OL',   ts.cap_ol   FROM team_seasons ts JOIN seasons s USING (season)
    UNION ALL SELECT ts.season, ts.team_id, ts.wins * 17.0 / ts.games, s.salary_cap, 'EDGE', ts.cap_edge FROM team_seasons ts JOIN seasons s USING (season)
    UNION ALL SELECT ts.season, ts.team_id, ts.wins * 17.0 / ts.games, s.salary_cap, 'IDL',  ts.cap_idl  FROM team_seasons ts JOIN seasons s USING (season)
    UNION ALL SELECT ts.season, ts.team_id, ts.wins * 17.0 / ts.games, s.salary_cap, 'LB',   ts.cap_lb   FROM team_seasons ts JOIN seasons s USING (season)
    UNION ALL SELECT ts.season, ts.team_id, ts.wins * 17.0 / ts.games, s.salary_cap, 'CB',   ts.cap_cb   FROM team_seasons ts JOIN seasons s USING (season)
    UNION ALL SELECT ts.season, ts.team_id, ts.wins * 17.0 / ts.games, s.salary_cap, 'S',    ts.cap_s    FROM team_seasons ts JOIN seasons s USING (season)
),
thirds AS (
    SELECT
        pos,
        wins_17,
        cap / salary_cap AS cap_share,
        NTILE(3) OVER (PARTITION BY pos ORDER BY cap / salary_cap) AS spend_third
    FROM spend
)
SELECT
    pos                                                                    AS position_group,
    ROUND(100 * AVG(CASE WHEN spend_third = 3 THEN cap_share END), 1)      AS top_third_cap_pct,
    ROUND(AVG(CASE WHEN spend_third = 3 THEN wins_17 END), 1)              AS top_third_wins,
    ROUND(100 * AVG(CASE WHEN spend_third = 1 THEN cap_share END), 1)      AS bottom_third_cap_pct,
    ROUND(AVG(CASE WHEN spend_third = 1 THEN wins_17 END), 1)              AS bottom_third_wins,
    ROUND(AVG(CASE WHEN spend_third = 3 THEN wins_17 END)
        - AVG(CASE WHEN spend_third = 1 THEN wins_17 END), 2)              AS win_gap
FROM thirds
GROUP BY pos
ORDER BY win_gap DESC;
