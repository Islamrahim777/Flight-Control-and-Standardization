UAV Unit HR & Operations Analytics

An end-to-end data analytics portfolio project: a synthetic dataset modeling 525 personnel across 5 departments of a fictional UAV (drone) military unit (2021–2026), built to demonstrate the full analyst toolkit — Python for data generation and cleaning, SQL (SQLite, PostgreSQL, MySQL) for relational modeling and querying, Excel for formula-driven reporting, and Tableau for visualization.

All data is 100% synthetic. Names, IDs, ranks, and records are generated for demonstration purposes only and do not represent real people, units, or events.

## 📊 Interactive Dashboards (Tableau Public)

| # | Dashboard | Focus |
|---|---|---|
| 1 | [Sigma Paradox: Low Risk, Low Recognition](https://public.tableau.com/app/profile/islam.rahimov/viz/UAVUnitAnalytics-SigmaDepartmentDeepDive/SigmaParadoxLowRiskLowRecognition) | Department-level reward system inequity — Sigma has the lowest risk score yet the most under-recognized top performers |
| 2 | [Flight Hours for per Rank](https://public.tableau.com/app/profile/islam.rahimov/viz/FlightHoursforperrank/Dashboard3) | Methodology lesson: cumulative vs. last-12-month measurement changes the story |
| 3 | [Training Investment Pays Off](https://public.tableau.com/app/profile/islam.rahimov/viz/TrainingInvestmentPaysOff_17893185486170/TrainingInvestmentPaysOff) | Aviation School training advantage + first-shot learning curve effect |
| 4 | [Aircraft Reliability Declines With Age](https://public.tableau.com/app/profile/islam.rahimov/viz/AircraftReliabilityDeclinesWithAge_17893185902610/AircraftReliabilityDeclinesWithAge) | Fleet aging and in-flight technical problem rates |
| 5 | [Simpson's Paradox: When Aggregation Lies](https://public.tableau.com/app/profile/islam.rahimov/viz/SimpsonsParadoxWhenAggregationLies_17893186472610/SimpsonsParadoxWhenAggregationLies) | A real statistical paradox: the maintenance-reliability relationship reverses depending on aggregation level |
| 6 | [Annual Flight Hour Compliance Tracker](https://public.tableau.com/app/profile/islam.rahimov/viz/AnnualFlightHourComplianceTracker_2025/AnnualFlightHour_ComplianceTracker_2025) | **Interactive** — adjustable minimum-hours threshold parameter + dynamic department filtering |
| 7 | [Monthly Operations Dashboard](https://public.tableau.com/app/profile/islam.rahimov/viz/MonthlyOperationsDashboardFlightHoursFuelShootingTechnicalProblems/MonthlyOperationsDashboardFlightHoursFuelShootingTechnicalProblems) | **Interactive** — 4 synchronized charts (flight hours, fuel, shooting, technical problems), filterable by year/month |
| 8 | [Regional Performance Profile](https://public.tableau.com/app/profile/islam.rahimov/viz/RegionalPerformanceProfile/RegionalPerformanceProfile) | Recruitment region vs. shooting success, discipline rate, and rank composition |
| 9 | [Commissioning Source Effect by Role](https://public.tableau.com/app/profile/islam.rahimov/viz/CommissioningSourceEffectbyRole/Dashboard7) | Officer commissioning path performance varies by role — an actionable recruitment recommendation |

Most portfolio datasets are either too clean (no real analytical story) or too random (no findings to surface). This one is engineered the opposite way: every relationship in the data is intentional — some strong, some deliberately weak or noisy — so the analysis surfaces real, non-obvious findings, not just charts of random numbers.

Tech stack & pipeline
Python (generation + cleaning) → SQLite / PostgreSQL / MySQL (relational model)
                                → SQL (aggregation, window functions, set ops)
                                → Excel (formulas / QA)
                                → Tableau (9 dashboards, 2 fully interactive)
Python (scripts/) generates 21 interconnected tables with realistic constraints (rank-tenure consistency, crew rotation logic, seasonal flight patterns, aircraft aging) — see Data model below. scripts/data_cleaning/ demonstrates a full pandas cleaning pipeline (deduplication, text normalization, cross-table imputation) on a deliberately "dirtied" version of the personnel table.

**Python analysis notebook**: [`scripts/uav_python_analysis.ipynb`](scripts/uav_python_analysis.ipynb) recreates all key findings below using pandas, matplotlib, and seaborn — charts render directly on GitHub, no setup needed.
SQLite (database/uav_analytics.db) hosts all 21 tables with full foreign-key enforcement. PostgreSQL and MySQL setup scripts (sql/postgres_setup/) provide an alternative production-style setup, including course-style step-by-step schema/load scripts.
SQL (sql/portfolio_analysis/) — 6 organized files covering the full range of SQL techniques: aggregations and CASE logic, CTEs, window functions (ROW_NUMBER, LAG, NTILE, AVG() OVER), HAVING, NOT EXISTS, native CORR(), UNION/INTERSECT/EXCEPT, ROLLUP/GROUPING SETS, and a reusable CREATE VIEW.
Excel (excel/) — a formula-driven workbook (AVERAGEIF, INDEX/MATCH, conditional formatting) plus a readable monthly flight log report.
Tableau — 9 published dashboards (see table above), including two with parameters, calculated fields, and cross-filter dashboard actions.
Data model (24 tables)
Domain	Tables
Personnel	personal, rank_history, previous_service, rank_delay_analysis, certifications
Fitness & discipline	fitness_standards, physical_fitness, tactical_training, discipline_records
Flight operations	mission_log (crew-level), flight_operations (person-month rollup), mission_profile
Performance	shooting_performance, standardization_exams
Aircraft & maintenance	aircraft, aircraft_monthly_maintenance, mission_technical_log, fuel_consumption, flight_safety
Outcomes	medals, risk_score
Workforce planning	authorized_positions (staffing/vacancy rate), workforce_growth_plan (2027-2030 hiring projection), rank_hierarchy (unified seniority ordering)

Key design decisions:

Crew model: every mission has 1 pilot (full duration) plus UAV operators and mission commanders rotating in 4-hour shifts — not one person flying independently.
Aircraft aging: older airframes need more maintenance and develop more in-flight problems (individual hardware wears out over time).
Three officer-commissioning paths: Military Academy (incl. an Aviation School track), Civilian Direct Commission, and Prior-Enlisted (Gizir) Commission — each with different, role-dependent strengths baked into the data.
Intentionally weak correlations: medal counts correlate only weakly with actual performance (~0.03–0.12) — a deliberate "is the reward system fair?" finding, not a bug.
Repository structure
data/                       21 source CSVs (tidy/long format)
database/                   uav_analytics.db — SQLite, all tables + foreign keys
sql/
├── portfolio_analysis/     6 files: basics → findings → time series →
│                           correlations → window functions → set operations
└── postgres_setup/         Step-by-step PostgreSQL setup (create DB,
                            create tables, load data, add extra tables)
scripts/
├── generate_*.py           21 seeded, reproducible table generators
└── data_cleaning/          Dirty-data generator + pandas cleaning pipeline
excel/                      Formula-driven workbook + monthly flight log report
docs/
├── PROJECT_INSIGHTS.md     Full write-up of all findings, with numbers
└── tableau_dashboard_guide.md
Getting started

SQLite (fastest): open database/uav_analytics.db with any SQLite client (or sqlite3 database/uav_analytics.db) and run the queries in sql/portfolio_analysis/.

PostgreSQL: follow sql/postgres_setup/1_create_database.sql through 4_add_authorized_positions.sql in order (edit the file paths for your machine first).

Python: pip install pandas numpy then run any scripts/generate_*.py file to see how that table was built (all seeded for reproducibility). Run scripts/data_cleaning/data_cleaning_demo.py to see the cleaning pipeline in action.

Excel: open excel/uav_analytics_demo.xlsx — see the Dept_Summary and Risk_Watchlist sheets for formula examples.

Tableau: the 9 dashboards linked above are live on Tableau Public — no setup needed to view them.

Key findings

Full write-up with exact figures in docs/PROJECT_INSIGHTS.md. Highlights:

Methodology matters as much as the data: rank vs. flight hours shows no relationship measured as lifetime cumulative hours (confounded by tenure), but a clear decline when measured as last-12-months hours.
Simpson's Paradox: maintenance hours and technical-problem rates appear positively correlated at the department-year level — but the true, individual aircraft-month relationship is negative. Fleet aging is the hidden confounder.
Reward-system inequity is concentrated in one department: Sigma combines the lowest risk score of any department with the highest share of under-recognized top performers — a structural, not behavioral, problem.
Commissioning path effects are role-specific: Civilian-commissioned officers match other paths as Pilot-Operators (88%) but underperform as Operations Officers (73%) — a targeted recruitment insight, not a blanket "path X is better" conclusion.
First-shot effect: success rate jumps from 58% (first live shot) to 88% (all subsequent shots) — a measurable practice effect.
Aircraft reliability: in-flight problem rates roughly double from age 0 to age 5, supporting proactive fleet-replacement planning.
