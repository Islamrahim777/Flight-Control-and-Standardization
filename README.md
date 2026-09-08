# UAV Unit HR & Operations Analytics

An end-to-end data analytics portfolio project: a synthetic dataset modeling
525 personnel across 5 departments of a fictional UAV (drone) military unit
(2021–2026), built to demonstrate the full analyst toolkit — **Python** for
data generation, **SQL** for relational modeling and querying, **Excel**
for formula-driven reporting, and **Tableau** for visualization.

> **All data is 100% synthetic.** Names, IDs, ranks, and records are
> generated for demonstration purposes only and do not represent real
> people, units, or events.

## Why this project

Most portfolio datasets are either too clean (no real analytical story) or
too random (no findings to surface). This one is engineered the opposite
way: **every relationship in the data is intentional** — some strong,
some deliberately weak or noisy — so that the analysis has real,
non-obvious findings to uncover, not just charts of random numbers.

## Tech stack & pipeline

```
Python (generation) → SQLite (relational model) → SQL (aggregation)
                                                  → Excel (formulas/QA)
                                                  → Tableau (dashboards)
```

1. **Python** (`scripts/`) generates 21 interconnected tables with
   realistic constraints (rank-tenure consistency, crew rotation logic,
   seasonal flight patterns, aircraft aging) — see *Data model* below.
2. **SQLite** (`database/uav_analytics.db`) hosts all 21 tables with full
   foreign-key enforcement.
3. **SQL** (`sql/example_queries.sql`) — example queries for department
   comparisons, medal/performance mismatches, and data-quality checks.
   Year/person/department roll-ups are intentionally **not**
   pre-computed — that aggregation is left as the analytical exercise.
4. **Excel** (`excel/`) — a formula-driven workbook (`AVERAGEIF`,
   `INDEX/MATCH`, conditional formatting) plus a readable monthly flight
   log report.
5. **Tableau** — see `docs/tableau_dashboard_guide.md` for a field-by-field
   guide to building 5 dashboards from the raw CSVs in `data/`.

## Data model (21 tables)

| Domain | Tables |
|---|---|
| Personnel | `personal`, `rank_history`, `previous_service`, `rank_delay_analysis`, `certifications` |
| Fitness & discipline | `fitness_standards`, `physical_fitness`, `tactical_training`, `discipline_records` |
| Flight operations | `mission_log` (crew-level), `flight_operations` (person-month rollup), `mission_profile` |
| Performance | `shooting_performance`, `standardization_exams` |
| Aircraft & maintenance | `aircraft`, `aircraft_monthly_maintenance`, `mission_technical_log`, `fuel_consumption`, `flight_safety` |
| Outcomes | `medals`, `risk_score` |

**Key design decisions:**
- **Crew model**: every mission has 1 pilot (full duration) plus UAV
  operators and mission commanders rotating in 4-hour shifts — not one
  person flying independently.
- **Aircraft aging**: older airframes need more maintenance and develop
  more in-flight problems (the opposite of an organizational "learning
  curve" — individual hardware wears out).
- **Three officer-commissioning paths**: Military Academy (incl. an
  Aviation School track), Civilian Direct Commission, and Prior-Enlisted
  (Gizir) Commission — each with different strengths/weaknesses baked in.
- **Intentionally weak correlations**: medal counts correlate only
  weakly with actual performance (~0.03–0.12) — a deliberate "is the
  reward system fair?" finding, not a bug.

## Repository structure

```
data/       21 CSVs — the source-of-truth tables (tidy/long format)
database/   uav_analytics.db — SQLite, all tables + foreign keys
sql/        example_queries.sql — starter queries
scripts/    Python generators for every table (re-runnable, seeded)
excel/      Formula-driven workbook + monthly flight log report
docs/       Tableau dashboard build guide
```

## Getting started

**SQL:** open `database/uav_analytics.db` with any SQLite client (or
`sqlite3 database/uav_analytics.db`) and run the queries in
`sql/example_queries.sql`.

**Python:** `pip install pandas numpy` then run any `scripts/generate_*.py`
file to see how that table was built (all seeded for reproducibility).

**Excel:** open `excel/uav_analytics_demo.xlsx` — see the `Dept_Summary`
and `Risk_Watchlist` sheets for formula examples.

**Tableau:** connect to the CSVs in `data/` and follow
`docs/tableau_dashboard_guide.md`.

## Example findings

- Rank vs. flight activity shows **no relationship** when measured as
  lifetime cumulative hours (confounded by tenure) but a clear
  **negative relationship** (-0.34) when measured as last-12-months
  hours — a good illustration of why methodology matters.
- First-shot success rate (~61%) is substantially lower than subsequent
  shots (~89%) — a measurable "first-attempt" effect.
- Aircraft in-flight problem rates roughly double from age 0 to age 6,
  while pre/post-flight inspection time grows from ~1 hour to ~2 hours
  over the same span.
