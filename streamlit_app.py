"""GridironCapIQ: how NFL teams spend a fixed salary cap, and what it buys.

Run locally:  streamlit run streamlit_app.py
Reads data/gridironcapiq.db (build it with src/build_database.py).
"""
import sqlite3
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
DB_PATH = ROOT / "data" / "gridironcapiq.db"
SQL_DIR = ROOT / "sql" / "analysis"

# Position groups in display order, with the team_seasons column that holds each one
POSITIONS = {
    "QB": "cap_qb", "RB": "cap_rb", "WR": "cap_wr", "TE": "cap_te", "OL": "cap_ol",
    "EDGE": "cap_edge", "IDL": "cap_idl", "LB": "cap_lb", "CB": "cap_cb", "S": "cap_s",
    "Special teams": "cap_st",
}
BLUE = "#2a78d6"      # selected team
GRAY = "#9a9a94"      # league average and other teams

st.set_page_config(page_title="GridironCapIQ", layout="wide")


@st.cache_data
def query(sql):
    """Run a SQL string against the database and return a DataFrame."""
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
        return pd.read_sql(sql, conn)


@st.cache_data
def run_file(name):
    """Run one of the analysis queries in sql/analysis/."""
    return query((SQL_DIR / name).read_text())


@st.cache_data
def load_team_seasons():
    return query("""
        SELECT ts.*, t.team_name, s.salary_cap
        FROM team_seasons ts
        JOIN teams t ON t.team_id = ts.team_id
        JOIN seasons s ON s.season = ts.season
    """)


if not DB_PATH.exists():
    st.error("Database not found. Run `python src/build_database.py` first.")
    st.stop()

data = load_team_seasons()
data["wins_17"] = data["wins"] * 17 / data["games"]
data["cap_share_pct"] = 100 * data["cap_total"] / data["salary_cap"]
first_season, last_season = int(data["season"].min()), int(data["season"].max())

# ---------------------------------------------------------------- header
st.title("GridironCapIQ")
st.write(
    "Every NFL team plays under roughly the same salary cap, yet results vary widely. "
    f"This dashboard looks at how teams divided that cap across positions from {first_season} "
    f"to {last_season}, and how that lines up with winning."
)

# ---------------------------------------------------------------- key findings
st.header("Key findings")

qb = run_file("01_qb_cap_vs_wins.sql").set_index("qb_cap_band")
pos_gap = run_file("06_position_spend_vs_wins.sql").set_index("position_group")
rookie = run_file("03_rookie_deals_vs_wins.sql").set_index("rookie_cap_band")

qb_mid = qb.loc["3) 10-15%"]
qb_low = qb.loc[["1) under 5%", "2) 5-10%"]]
qb_low_wins = (qb_low["avg_wins_per_17"] * qb_low["team_seasons"]).sum() / qb_low["team_seasons"].sum()
rookie_hi, rookie_lo = rookie.loc["4) 32% or more"], rookie.loc["1) under 22%"]
top_pos = pos_gap.head(3)

f1, f2, f3 = st.columns(3)
with f1:
    st.metric("QB at 10-15% of the cap", f"{qb_mid['avg_wins_per_17']:.1f} wins",
              f"{qb_mid['avg_wins_per_17'] - qb_low_wins:+.1f} vs teams under 10%")
    st.caption("Paying a quarterback a mid-sized share goes with about a win more. Paying past 15% adds nothing.")
with f2:
    st.metric("Running back spending: win gap", f"{pos_gap.loc['RB', 'win_gap']:+.2f} wins")
    st.caption(
        f"Big RB spenders win no more than low spenders (top vs bottom third). The biggest gaps are at {', '.join(top_pos.index[:3])}, "
        "and even those are under one win."
    )
with f3:
    st.metric("Heavy rookie-deal rosters", f"{rookie_hi['avg_wins_per_17']:.1f} wins",
              f"{rookie_hi['avg_wins_per_17'] - rookie_lo['avg_wins_per_17']:+.1f} vs under 22% of cap",
              delta_color="off")
    st.caption("Teams that put 32% or more of their cap on first-4-year players win less. "
               "That is likely a symptom of thin veteran rosters, not a cause.")

st.caption("These are correlations across team-seasons, not proof of cause. Good players get paid because they win.")

# ---------------------------------------------------------------- pickers
st.header("Explore a team")
c1, c2 = st.columns(2)
season = c1.selectbox("Season", sorted(data["season"].unique(), reverse=True))
season_rows = data[data["season"] == season].sort_values("team_name")
team_name = c2.selectbox("Team", season_rows["team_name"].tolist())
team = season_rows[season_rows["team_name"] == team_name].iloc[0]

m1, m2, m3 = st.columns(3)
m1.metric("Record", f"{int(team['wins'])}-{int(team['games'] - team['wins'] - team['ties'])}"
          + (f"-{int(team['ties'])}" if team["ties"] else ""))
rank = int(season_rows["wins"].rank(ascending=False, method="min")[team.name])
m2.metric("Wins rank", f"{rank} of {len(season_rows)}")
m3.metric("QB share of tracked cap", f"{100 * team['qb_cap_pct']:.1f}%")

# ---------------------------------------------------------------- cap by position
st.subheader(f"Where the {team_name} spent their cap, {season}")
st.caption("Share of each team's tracked cap hits, by position group, against the league average that season.")

rows = []
for label, col in POSITIONS.items():
    rows.append({"Position": label, "Series": team_name,
                 "Share": 100 * team[col] / team["cap_total"]})
    rows.append({"Position": label, "Series": "League average",
                 "Share": (100 * season_rows[col] / season_rows["cap_total"]).mean()})
bars = pd.DataFrame(rows)

chart = (
    alt.Chart(bars)
    .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
    .encode(
        x=alt.X("Position:N", sort=list(POSITIONS), axis=alt.Axis(labelAngle=0, title=None)),
        xOffset=alt.XOffset("Series:N", sort=[team_name, "League average"]),
        y=alt.Y("Share:Q", title="% of tracked cap"),
        color=alt.Color("Series:N", sort=[team_name, "League average"],
                        scale=alt.Scale(domain=[team_name, "League average"], range=[BLUE, GRAY]),
                        legend=alt.Legend(orient="top", title=None)),
        tooltip=["Position", "Series", alt.Tooltip("Share:Q", format=".1f", title="% of cap")],
    )
    .properties(height=320)
)
st.altair_chart(chart, width="stretch")

with st.expander("Show as a table"):
    table = bars.pivot(index="Position", columns="Series", values="Share").reindex(list(POSITIONS)).round(1)
    st.dataframe(table, width="stretch")

# ---------------------------------------------------------------- QB scatter
st.subheader("Quarterback spending vs wins")
st.caption(f"Each dot is one team-season, {first_season} to {last_season}. "
           f"Blue dots are the {team_name} in other seasons; the large dot is {season}.")

scatter_data = data.assign(
    qb_pct=100 * data["qb_cap_pct"],
    Group=lambda d: (d["team_id"] == team["team_id"]).map({True: "Selected team", False: "Other teams"}),
)
base = alt.Chart(scatter_data).encode(
    x=alt.X("qb_pct:Q", title="QB share of tracked cap (%)", scale=alt.Scale(zero=False)),
    y=alt.Y("wins:Q", title="Regular-season wins", scale=alt.Scale(domain=[0, 17])),
    tooltip=[alt.Tooltip("team_name:N", title="Team"), alt.Tooltip("season:O", title="Season"),
             alt.Tooltip("wins:Q", title="Wins"), alt.Tooltip("qb_pct:Q", format=".1f", title="QB % of cap")],
)
others = base.transform_filter(alt.datum.Group == "Other teams").mark_circle(size=40, color=GRAY, opacity=0.4)
mine = base.transform_filter(alt.datum.Group == "Selected team").mark_circle(size=70, color=BLUE, opacity=0.9)
highlight = (
    alt.Chart(scatter_data[(scatter_data["team_id"] == team["team_id"]) & (scatter_data["season"] == season)])
    .mark_circle(size=220, color=BLUE, stroke="#fcfcfb", strokeWidth=2)
    .encode(x="qb_pct:Q", y="wins:Q")
)
st.altair_chart((others + mine + highlight).properties(height=360), width="stretch")

# ---------------------------------------------------------------- rankings
st.subheader("Wins for the cap spent: team rankings")
scope = st.radio("Show", [f"{season} season", f"All seasons, {first_season}-{last_season}"], horizontal=True)
pool = season_rows if scope.startswith(str(season)) else data
rank_df = (
    pool.groupby("team_name")
    .agg(wins=("wins_17", "mean"), cap_share=("cap_share_pct", "mean"))
    .assign(per_10=lambda d: d["wins"] / (d["cap_share"] / 10))
    .sort_values("per_10", ascending=False)
    .reset_index()
)
rank_df.insert(0, "Rank", range(1, len(rank_df) + 1))
st.dataframe(
    rank_df.rename(columns={"team_name": "Team", "wins": "Avg wins (per 17)",
                            "cap_share": "Tracked cap share (%)", "per_10": "Wins per 10 pts of cap"}),
    hide_index=True, width="stretch", height=36 * (len(rank_df) + 1) + 3,
    column_config={
        "Avg wins (per 17)": st.column_config.NumberColumn(format="%.1f"),
        "Tracked cap share (%)": st.column_config.NumberColumn(format="%.1f"),
        "Wins per 10 pts of cap": st.column_config.ProgressColumn(
            format="%.2f", min_value=0, max_value=float(rank_df["per_10"].max())),
    },
)
st.caption(
    "Read this with care. Tracked cap share differs by team (and more in a single season) because the data "
    "does not capture every contract or any dead money, so a team can look efficient partly because less of its "
    "cap is tracked. Over all seasons the ranking is mostly a ranking by wins."
)

# ---------------------------------------------------------------- notes
with st.expander("About the data"):
    st.markdown(
        "- Data: [nflverse](https://github.com/nflverse) (contract data sourced from OverTheCap.com), "
        f"regular seasons {first_season}-{last_season}.\n"
        "- Cap spending is each player's real cap hit that season. It covers about 79-89% of each team's "
        "full cap and excludes dead money, so compare teams by share, not raw dollars.\n"
        "- Wins are regular-season wins, scaled to 17 games where seasons were 16 games.\n"
        "- Built with Python, SQLite and Streamlit. Code: "
        "[github.com/floresandflores/GridironCapIQ](https://github.com/floresandflores/GridironCapIQ)."
    )
