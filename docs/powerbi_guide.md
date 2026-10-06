# Building GridironCapIQ in Power BI

This guide rebuilds the Streamlit dashboard in **Power BI Desktop** (Windows). The Streamlit app stays live; the Power BI report is a second version of the same analysis, built on the same data.

You will end with a `.pbix` report with three pages:

```
Page 1: Key findings      Page 2: Explore a team                 Page 3: Team rankings
┌──────────────────────┐  ┌──────────────────────────────────┐  ┌──────────────────────┐
│ QB band   │ Rookie   │  │ [Season ▾] [Team ▾]              │  │ [Seasons ▾]          │
│ bar chart │ band bar │  │ Record │ Wins rank │ QB share    │  │ Team  Wins  Cap  W/10│
├───────────┴──────────┤  │ Cap by position vs league avg    │  │ ...   ...   ...  ███ │
│ Win gap by position  │  │ QB share vs wins (scatter)       │  │ ...   ...   ...  ██  │
└──────────────────────┘  └──────────────────────────────────┘  └──────────────────────┘
```

## Step 0: Get the data files

Power BI can't open SQLite, so `src/export_powerbi.py` exports the database to CSVs in [`data/powerbi/`](../data/powerbi/). The weekly refresh job re-runs it, so the CSVs stay current.

Download the repo as a ZIP from GitHub (Code → Download ZIP), unzip it, and note where the `data/powerbi` folder is.

| File | One row per | Role |
|---|---|---|
| `teams.csv` | team | lookup (dimension) |
| `seasons.csv` | season, 2013-2025 | lookup |
| `positions.csv` | position group | lookup, gives the display order |
| `team_seasons.csv` | team per season | fact: wins, record, cap totals, QB share |
| `position_cap.csv` | team per season per position | fact: cap spent at each position |
| `findings_*.csv` | band or position | results of the SQL analysis queries |

Money is in $ millions. Percentages are fractions (`0.12` means 12%), which is what Power BI expects before you format a column as a percentage.

## Step 1: Load the CSVs

1. Open Power BI Desktop → **Get data → Text/CSV** → pick `teams.csv` → **Load**.
2. Repeat for the other seven files. (Faster: **Get data → Folder**, but that combines files into one table, which is not what we want here.)
3. In the **Data** view, check a few types: `season` should be a whole number, every `*_share` column a decimal number.
4. For each `*_share` column, select it and set **Column tools → Format → Percentage**, 1 decimal place.
5. Select `season` in every table and set **Summarization → Don't summarize**, so Power BI doesn't try to add up years.

## Step 2: Build the data model

Go to **Model view**. Power BI may have guessed some relationships; delete any you didn't expect and make these five (drag a column onto the matching column):

| From (one side) | To (many side) |
|---|---|
| `teams[team_id]` | `team_seasons[team_id]` |
| `teams[team_id]` | `position_cap[team_id]` |
| `seasons[season]` | `team_seasons[season]` |
| `seasons[season]` | `position_cap[season]` |
| `positions[position]` | `position_cap[position]` |

This is a **star schema**: lookup tables around fact tables, every relationship one-to-many, filters flowing from the lookup to the fact. It's the same idea as the foreign keys in `sql/schema.sql`.

Then:
- Select `positions[position]` → **Column tools → Sort by column → sort_order**, so charts show QB, RB, WR... instead of alphabetical.
- Hide `team_id`, `season` and `position` in the two fact tables (right-click → Hide in report view). Report builders then always pick from the lookup tables, which is what makes slicers filter both fact tables at once.

The `findings_*` tables stay unconnected; they're already summarized.

## Step 3: Write the measures (DAX)

A **measure** is a formula that's recalculated for whatever the visual is showing (a team, a season, a position). Create a table to hold them: **Home → Enter data**, name it `_Measures`, load it. Then select it and use **New measure** for each one below.

The first one, line by line:

```DAX
Team Cap Share =
DIVIDE(
    SUM(position_cap[cap_m]),
    CALCULATE(SUM(position_cap[cap_m]), REMOVEFILTERS(positions))
)
```

- `SUM(position_cap[cap_m])`: dollars spent in the current filter, e.g. Chiefs + 2024 + QB.
- `CALCULATE(..., REMOVEFILTERS(positions))`: the same sum with the position filter removed, so Chiefs + 2024 + all positions.
- `DIVIDE(a, b)`: a ÷ b, returning blank instead of an error if b is 0.

Result: the share of that team's tracked cap going to that position, same as the blue bars in Streamlit. Format it as a percentage.

The rest:

```DAX
League Avg Share =
CALCULATE(
    AVERAGEX(VALUES(position_cap[team_id]), [Team Cap Share]),
    REMOVEFILTERS(teams)
)
```
Removes the team filter, then averages `Team Cap Share` across all 32 teams for the same season and position (the gray bars).

```DAX
Record =
SUM(team_seasons[wins]) & "-" & SUM(team_seasons[losses])
    & IF(SUM(team_seasons[ties]) > 0, "-" & SUM(team_seasons[ties]))

Wins Rank =
RANKX(ALL(teams), CALCULATE(SUM(team_seasons[wins])), , DESC)

QB Share = AVERAGE(team_seasons[qb_share_of_tracked])

Avg Wins per 17 = AVERAGE(team_seasons[wins_per_17])

Avg Tracked Cap Share = AVERAGE(team_seasons[tracked_cap_share])

Wins per 10 pts of Cap = DIVIDE([Avg Wins per 17], [Avg Tracked Cap Share] * 10)
```

`Wins per 10 pts of Cap` multiplies by 10 because the share is a fraction: 0.85 becomes 8.5 "ten-point" units. A team averaging 9 wins on 85% tracked cap scores 9 ÷ 8.5 = 1.06.

## Step 4: Page 1, Key findings

Rename the page "Key findings". Add a text box at the top with the question: *How do winning NFL teams divide the same salary cap differently from losing ones?*

1. **QB spending**: Clustered column chart. X-axis `findings_qb_bands[qb_cap_band]`, Y-axis `avg_wins_per_17` (set to Don't summarize, or use Average). Title: "Paying a QB 10-15% of the cap goes with about one more win".
2. **Rookie deals**: Same chart type with `findings_rookie_bands`. Title: "Rosters heavy on rookie deals win less (likely a symptom of thin veteran talent)".
3. **Position gaps**: Bar chart (horizontal). Y-axis `findings_position_gaps[position_group]`, X-axis `win_gap`, sorted descending. Title: "No position's spending is worth even a full win".
4. Add a small text box: *Correlations across 416 team-seasons, 2013-2025, not proof of cause.*

The band labels start with `1)`, `2)`... so they sort correctly as text, the same trick as in the SQL.

## Step 5: Page 2, Explore a team

1. **Slicers**: Add a slicer with `seasons[season]` and one with `teams[team_name]`. For both: **Format → Slicer settings → Style: Dropdown**, and turn on **Single select**.
2. **Cards**: Three card visuals with `Record`, `Wins Rank`, `QB Share`.
3. **Cap by position vs league average**: Clustered column chart. X-axis `positions[position]`; Y-axis `Team Cap Share` and `League Avg Share`. Color the team series blue (`#2a78d6`) and the league average gray (`#9a9a94`).
4. **QB share vs wins**: Scatter chart. X-axis `team_seasons[qb_share_of_tracked]` (Average), Y-axis `team_seasons[wins]` (Average), Values `teams[team_name]` and `seasons[season]` so each dot is one team-season. Right now the slicers shrink it to one dot. Fix that: select the season slicer → **Format → Edit interactions** → click the ⦸ (None) icon above the scatter. Do the same for the team slicer. Now the scatter shows every team-season again.

## Step 6: Page 3, Team rankings

1. Add a `seasons[season]` slicer (List style, multi-select, with **Select all** on), so you can look at one season or all of them.
2. Add a **Table** visual: `teams[team_name]`, `Avg Wins per 17`, `Avg Tracked Cap Share`, `Wins per 10 pts of Cap`. Sort by the last column, descending.
3. Select the table → **Format → Cell elements** → turn on **Data bars** for `Wins per 10 pts of Cap`.
4. Add the same warning as the Streamlit app: tracked cap share differs by team because the data misses some contracts and all dead money, so read the ranking with care.

## Step 7: Finish and share

- **View → Themes**: pick a plain light theme to match the Streamlit design (no team colors).
- Save as `GridironCapIQ.pbix`.
- Optional: **Publish** to the Power BI service, or take screenshots of each page for the README.
- To refresh with new data: re-run `python src/export_powerbi.py` (or download the latest ZIP), then **Home → Refresh**.

## Stretch goals

- **Highlight the selected team in the scatter.** Make a disconnected table `Team Picker = DISTINCT(teams[team_name])`, use it in the team slicer, and color dots with a measure that compares each dot's team to `SELECTEDVALUE('Team Picker'[team_name])`.
- **Conference/division slicer** on the rankings page, using `teams[conference]` and `teams[division]`.

## Practice questions

**1. Why do `team_seasons` and `position_cap` both connect to `teams` instead of to each other?**
- A) Power BI can't connect two fact tables
- B) So one team slicer filters both fact tables through the shared lookup table
- C) It makes the CSV files smaller
- D) The relationship would be one-to-one

**2. In `Team Cap Share`, what would happen if you deleted `REMOVEFILTERS(positions)`?**
- A) Every bar would show 100%, because the bottom of the fraction would be filtered to the same position as the top
- B) Every bar would show 0%
- C) The chart would show the league average instead
- D) Nothing would change

<details><summary>Answers</summary>

1. **B.** Filters flow from the "one" side to the "many" side, so a lookup table is the hub that lets one slicer reach every fact table.
2. **A.** Without it, the denominator also has the QB (or RB...) filter, so it equals the numerator.
</details>
