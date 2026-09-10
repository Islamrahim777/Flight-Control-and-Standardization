
/





























5 advanced sql techniques · SQL
-- ============================================================
-- 5_advanced_sql_techniques.sql
-- Demonstrating a broader range of SQL techniques: window functions,
-- HAVING, views, EXISTS, native correlation, and pivoting.
-- ============================================================
 
-- Query 1: Top 3 pilots by total flight hours, WITHIN each department
-- (Window function: ROW_NUMBER() OVER PARTITION BY)
WITH person_totals AS (
    SELECT department, person_id, SUM(flight_hours_real) AS total_hours
    FROM flight_operations
    GROUP BY department, person_id
),
ranked AS (
    SELECT
        department, person_id, total_hours,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY total_hours DESC) AS rank_in_dept
    FROM person_totals
)
SELECT department, person_id, total_hours, rank_in_dept
FROM ranked
WHERE rank_in_dept <= 3
ORDER BY department, rank_in_dept;
 
 
-- Query 2: Year-over-year flight hours change by department
-- (Window function: LAG() to compare each row to the previous year)
-- NOTE: 2026 only has 6 months of data (Jan-Jun), so its "decline" vs 2025
-- is a partial-year artifact, not a real drop — always check for this
-- before reporting a window-function trend.
SELECT
    department,
    year,
    SUM(flight_hours_real) AS total_hours,
    LAG(SUM(flight_hours_real)) OVER (PARTITION BY department ORDER BY year) AS prev_year_hours,
    ROUND(
        (SUM(flight_hours_real) - LAG(SUM(flight_hours_real)) OVER (PARTITION BY department ORDER BY year))
        * 100.0 / LAG(SUM(flight_hours_real)) OVER (PARTITION BY department ORDER BY year)
    , 1) AS pct_change_vs_prev_year
FROM flight_operations
GROUP BY department, year
ORDER BY department, year;
 
 
-- Query 3: Each person's flight hours vs. their department's average
-- (Window function: AVG() OVER PARTITION BY, without collapsing rows —
--  the key difference between a window function and GROUP BY)
SELECT
    person_id,
    department,
    SUM(flight_hours_real) AS person_total_hours,
    ROUND(AVG(SUM(flight_hours_real)) OVER (PARTITION BY department), 1) AS dept_avg_hours,
    ROUND(SUM(flight_hours_real) - AVG(SUM(flight_hours_real)) OVER (PARTITION BY department), 1) AS diff_from_dept_avg
FROM flight_operations
GROUP BY person_id, department
ORDER BY department, diff_from_dept_avg DESC;
 
 
-- Query 4: Departments where the average risk score exceeds the unit-wide average
-- (HAVING: filtering on an aggregate result, which WHERE cannot do)
SELECT department, ROUND(AVG(risk_score), 1) AS avg_dept_risk
FROM risk_score
GROUP BY department
HAVING AVG(risk_score) > (SELECT AVG(risk_score) FROM risk_score)
ORDER BY avg_dept_risk DESC;
 
 
-- Query 5: People who have NEVER received a medal
-- (NOT EXISTS: a correlated subquery, often clearer than LEFT JOIN + IS NULL)
SELECT personal.person_id, personal.first_name, personal.last_name, personal.department
FROM personal
WHERE NOT EXISTS (
    SELECT 1 FROM medals WHERE medals.person_id = personal.person_id
)
ORDER BY personal.department;
 
 
-- Query 6: Native Pearson correlation coefficients (PostgreSQL's built-in CORR())
-- Cross-checks the "eyeballed" relationships found earlier with a real statistic.
SELECT
    ROUND(CORR(person_hours.total_hours, person_success.success_rate)::numeric, 3)
        AS corr_flight_hours_vs_success_rate
FROM (
    SELECT person_id, SUM(flight_hours_real) AS total_hours
    FROM flight_operations GROUP BY person_id
) person_hours
JOIN (
    SELECT person_id, COUNT(*) FILTER (WHERE outcome = 'Successful') * 100.0 / COUNT(*) AS success_rate
    FROM shooting_performance GROUP BY person_id
) person_success ON person_hours.person_id = person_success.person_id;
 
SELECT
    ROUND(CORR(aircraft_age_years, had_inflight_technical_problem::int)::numeric, 3)
        AS corr_aircraft_age_vs_problem
FROM mission_technical_log;
 
/* Finding: CORR() confirms both relationships are genuinely weak at the
   individual-record level (flight hours vs. success rate: r=0.073;
   aircraft age vs. problem occurrence: r=0.053) — even though the
   aggregated problem RATE nearly doubles from age 0 (9.1%) to age 5
   (16.0%). This is an important nuance: a weak point-level correlation and
   a clear rate trend by bucket can both be true at once, because a low
   Pearson r reflects a lot of person-to-person/mission-to-mission noise
   around a real but modest underlying trend. Always report both the
   correlation coefficient AND the bucketed rates — neither alone tells
   the full story. */
 
 
-- Query 7: Quartile segmentation of personnel by flight hours
-- (Window function: NTILE — splits ranked rows into N equal-sized buckets)
WITH person_totals AS (
    SELECT person_id, SUM(flight_hours_real) AS total_hours
    FROM flight_operations
    GROUP BY person_id
)
SELECT
    NTILE(4) OVER (ORDER BY total_hours) AS flight_hours_quartile,
    COUNT(*) AS num_people,
    MIN(total_hours) AS min_hours_in_quartile,
    MAX(total_hours) AS max_hours_in_quartile
FROM person_totals
GROUP BY flight_hours_quartile
ORDER BY flight_hours_quartile;
 
 
-- Query 8: Pivot flight hours by department, with years as columns
-- (Manual pivot using CASE inside aggregate functions — the standard SQL
--  way to turn rows into columns without a database-specific PIVOT clause)
SELECT
    department,
    SUM(CASE WHEN year = 2021 THEN flight_hours_real ELSE 0 END) AS y2021,
    SUM(CASE WHEN year = 2022 THEN flight_hours_real ELSE 0 END) AS y2022,
    SUM(CASE WHEN year = 2023 THEN flight_hours_real ELSE 0 END) AS y2023,
    SUM(CASE WHEN year = 2024 THEN flight_hours_real ELSE 0 END) AS y2024,
    SUM(CASE WHEN year = 2025 THEN flight_hours_real ELSE 0 END) AS y2025,
    SUM(CASE WHEN year = 2026 THEN flight_hours_real ELSE 0 END) AS y2026_partial
FROM flight_operations
GROUP BY department
ORDER BY department;
 
 
-- Query 9: A reusable VIEW combining several department-level KPIs
-- (Views package a complex query as a virtual table other queries/BI
--  tools can simply SELECT FROM, without repeating the underlying logic.)
--
-- IMPORTANT: each source table is pre-aggregated to ONE ROW PER DEPARTMENT
-- in its own CTE before joining. Joining the raw tables directly on
-- department alone would fan out (e.g. Sigma has 105 risk_score rows and
-- 43 discipline_records rows -> a naive join produces 105*43 = 4,515
-- rows for Sigma alone, silently corrupting every COUNT/AVG downstream).
CREATE OR REPLACE VIEW department_scorecard AS
WITH risk_agg AS (
    SELECT department, ROUND(AVG(risk_score), 1) AS avg_risk_score
    FROM risk_score GROUP BY department
),
discipline_agg AS (
    SELECT department, COUNT(*) FILTER (WHERE record_type IN ('Reprimand','Warning')) AS discipline_incidents
    FROM discipline_records GROUP BY department
),
medal_agg AS (
    SELECT department, COUNT(*) AS total_medals
    FROM medals GROUP BY department
),
condition_agg AS (
    SELECT department, ROUND(AVG(effective_condition_score), 1) AS avg_aircraft_condition
    FROM mission_technical_log GROUP BY department
)
SELECT
    mp.department,
    risk_agg.avg_risk_score,
    discipline_agg.discipline_incidents,
    medal_agg.total_medals,
    condition_agg.avg_aircraft_condition
FROM mission_profile mp
LEFT JOIN risk_agg ON risk_agg.department = mp.department
LEFT JOIN discipline_agg ON discipline_agg.department = mp.department
LEFT JOIN medal_agg ON medal_agg.department = mp.department
LEFT JOIN condition_agg ON condition_agg.department = mp.department;
 
-- Once created, the view can be queried like any table:
SELECT * FROM department_scorecard ORDER BY avg_risk_score DESC;
 
