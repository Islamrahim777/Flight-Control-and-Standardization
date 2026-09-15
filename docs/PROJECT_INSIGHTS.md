# UAV HR & Operations Analytics — Project Insights Summary

## Project Overview
A synthetic, portfolio-quality dataset simulating HR and operational analytics
for a 525-person UAV (drone) military unit across 5 departments (Alpha, Beta,
Delta, Gamma, Sigma), spanning 2021–2026. Built end-to-end: Python data
generation → SQLite/PostgreSQL/MySQL → SQL analysis → (Tableau in progress).

**Tech stack:** Python (pandas, numpy), SQL (SQLite, PostgreSQL, MySQL),
Excel, Tableau, Git/GitHub.

**Scale:** 21 interconnected tables, ~90,000+ total records (largest table:
mission_log at ~52,800 rows).

---

## Key Findings

### 1. Methodology matters as much as the data (rank vs. flight hours)
Measuring **cumulative total** flight hours by rank shows little to no
pattern — senior officers simply have more tenure, so their totals pile up
regardless of current activity level. Restricting the same measure to the
**last 12 months only** reveals a clear decline: Lieutenants fly the most,
Lieutenant Colonels the least. **Lesson: the aggregation window can hide or
reveal a real trend.**

### 2. Reward system inequity is concentrated in one department
Among 17 people who combine elite performance (≥90% shooting success rate,
≥800 total flight hours) with minimal recognition (<2 medals), **29% (5 of
17) belong to Sigma department** — the highest concentration of any
department despite equal headcount across departments.

### 3. Sigma's weaknesses are structural, not behavioral
Despite having the **lowest** technical reliability score (avg. aircraft
condition 77.5 vs. 88–89 elsewhere) and the highest share of under-recognized
top performers, Sigma has the **fewest** discipline problems (25 incidents,
vs. Alpha's 36) and the **lowest** (best) average risk score (48.2) of all
five departments. Fixing Sigma requires equipment investment and reward
reform — not disciplinary action.

### 4. Aviation-specific training produces measurably better shooters
Officers from the Military Aviation School track: **91%** shooting success
rate. Officers from the General Military Academy: **81.8%**. A 9.2
percentage-point gap within the same broad "Military Academy" commissioning
category.

### 5. Military Academy graduates have far fewer discipline issues
Average negative discipline records per officer: Military Academy **0.17**,
Prior Enlisted (Gizir) Commission **0.40**, Civilian Direct Commission
**0.54** — roughly a 3x gap between the best and worst commissioning paths.

### 6. Fitness and discipline are weakly but measurably linked
People with a discipline record average **83.8** on fitness tests vs.
**87.6** for those with a clean record.

### 7. Strong first-attempt learning curve in marksmanship
First-shot success rate: **58.1%**. All subsequent shots: **87.6%** — a 29.5
percentage-point gap.

### 8. Aircraft age nearly doubles technical problem rates
In-flight technical problem rate rises from **9.1%** at age 0 to **16.0%**
at age 5.

### 9. Simpson's Paradox in maintenance vs. reliability
At the **department-year** level, maintenance hours and technical problem
rates appear *positively* correlated (+0.11) — misleadingly suggesting more
maintenance causes more problems. This is confounded by fleet aging (both
metrics rise together as the whole fleet gets older over time). At the
**individual aircraft-month** level, the true relationship is weakly
*negative* (−0.08), confirming maintenance genuinely helps. A textbook
example of why aggregation level can reverse an apparent relationship.

### 10. Flight/simulator hours don't predict shooting accuracy
People with 2000+ flight hours log ~3x more simulator time than those under
500 hours (273.2 vs. 88.7 avg. hours) — but nearly identical shooting
success rates (86.4% vs. 83.3%). Confirmed via native SQL `CORR()`: r=0.073
(flight hours vs. success) and r=0.053 (aircraft age vs. problem
occurrence) — both genuinely weak at the individual-record level, even
though bucketed/aggregated rates show clearer trends. **Both statistics are
true simultaneously and both are needed to tell the full story.**

### 11. Flight experience and marksmanship are largely separate skills
Of 46 "top flyers" (≥1,500 total flight hours) and 92 "top shooters" (≥90%
success rate), only **16 people qualify as both** (via SQL `INTERSECT`) —
most top flyers (30 of 46, via `EXCEPT`) are not also top shooters.

---

## SQL Techniques Demonstrated
Aggregations (COUNT/SUM/AVG/MIN/MAX), CASE WHEN, all JOIN types (INNER/LEFT),
multi-condition JOINs, CTEs (single & chained), `FILTER (WHERE ...)`,
date functions (`EXTRACT`, `TO_CHAR`), `COALESCE`, subqueries, `UNION` /
`UNION ALL` / `INTERSECT` / `EXCEPT`, `HAVING`, `NOT EXISTS` (correlated
subquery), window functions (`ROW_NUMBER`, `LAG`, `AVG() OVER PARTITION
BY`, `NTILE`), native `CORR()`, manual pivoting (`CASE` inside aggregates),
`ROLLUP`, `GROUPING SETS`, and `CREATE VIEW`.

---

## Repository Structure
```
uav-analytics-portfolio/
├── data/                  21 source CSVs
├── database/              SQLite (uav_analytics.db)
├── sql/
│   ├── portfolio_analysis/
│   │   ├── 1_basic_queries.sql
│   │   ├── 2_key_findings.sql
│   │   ├── 3_time_series_reports.sql
│   │   ├── 4_relationships_and_correlations.sql
│   │   ├── 5_advanced_sql_techniques.sql
│   │   └── 6_set_operations_and_grouping.sql
│   └── postgres_setup/    Course-style DB setup scripts (1-4)
├── scripts/                Python data generation (17 scripts)
├── scripts/data_cleaning/  Dirty-data + pandas cleaning demo
├── excel/
└── docs/
```
