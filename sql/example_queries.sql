-- ============================================================
-- UAV Unit Analytics — Example SQL Queries
-- Database: uav_analytics.db
-- ============================================================

-- 1) DEPARTMENT SCORECARD
-- Compares all 5 departments on flight activity, fuel efficiency,
-- shooting success, medals awarded, and average risk score.
SELECT
    p.department,
    ROUND(AVG(f.total_flight_hours_real), 0)      AS avg_annual_flight_hours,
    ROUND(AVG(f.fuel_burn_rate_l_per_hour), 2)     AS avg_fuel_burn_l_per_hour,
    ROUND(AVG(sh.success_rate), 3)                 AS avg_shooting_success_rate,
    ROUND(AVG(m.medal_count), 2)                   AS avg_medals_per_person,
    ROUND(AVG(r.risk_score), 1)                    AS avg_risk_score
FROM mission_profile p
LEFT JOIN fuel_consumption f ON f.department = p.department
LEFT JOIN (
    SELECT department, AVG(CASE WHEN outcome = 'Successful' THEN 1.0 ELSE 0.0 END) AS success_rate
    FROM shooting_performance GROUP BY department
) sh ON sh.department = p.department
LEFT JOIN (
    SELECT department, person_id, COUNT(*) AS medal_count
    FROM medals GROUP BY department, person_id
) m ON m.department = p.department
LEFT JOIN risk_score r ON r.department = p.department
GROUP BY p.department
ORDER BY avg_risk_score DESC;


-- 2) MEDAL vs PERFORMANCE MISMATCH
-- People with strong shooting success AND high flight hours,
-- but few (or zero) medals — the "reward system fairness" query.
SELECT
    pe.person_id, pe.department, pe.rank,
    ROUND(sh.success_rate, 3)   AS success_rate,
    ROUND(fl.total_hours, 0)    AS total_flight_hours,
    COALESCE(md.medal_count, 0) AS medal_count
FROM personal pe
JOIN (
    SELECT person_id, AVG(CASE WHEN outcome='Successful' THEN 1.0 ELSE 0.0 END) AS success_rate,
           COUNT(*) AS n_shots
    FROM shooting_performance GROUP BY person_id
) sh ON sh.person_id = pe.person_id
JOIN (
    SELECT person_id, SUM(flight_hours_real) AS total_hours
    FROM flight_operations GROUP BY person_id
) fl ON fl.person_id = pe.person_id
LEFT JOIN (
    SELECT person_id, COUNT(*) AS medal_count FROM medals GROUP BY person_id
) md ON md.person_id = pe.person_id
WHERE sh.success_rate >= 0.90 AND fl.total_hours >= 800
ORDER BY medal_count ASC, success_rate DESC
LIMIT 10;


-- 3) FIRST-SHOT FAILURE RATE
-- Compares outcome rate on a person's very first shot vs all later shots.
SELECT
    is_first_shot,
    COUNT(*)                                                  AS n_shots,
    ROUND(AVG(CASE WHEN outcome='Successful' THEN 1.0 ELSE 0.0 END), 3) AS success_rate
FROM shooting_performance
GROUP BY is_first_shot;


-- 4) RANK vs RECENT FLIGHT ACTIVITY
-- Does flight activity in the last 12 months fall as rank rises?
SELECT
    pe.rank,
    COUNT(DISTINCT pe.person_id)                    AS n_people,
    ROUND(AVG(fl.hours_12mo), 1)                    AS avg_hours_last_12mo
FROM personal pe
JOIN (
    SELECT person_id, SUM(flight_hours_real) AS hours_12mo
    FROM flight_operations
    WHERE (year = 2025 AND month > 6) OR (year = 2026 AND month <= 6)
    GROUP BY person_id
) fl ON fl.person_id = pe.person_id
WHERE pe.rank_group = 'Officer'
GROUP BY pe.rank
ORDER BY avg_hours_last_12mo DESC;


-- 5) RANK vs TENURE CONSISTENCY CHECK
-- Flags anyone whose total service years fall far outside the typical
-- range for their current rank (should return 0 rows if generation logic held).
SELECT person_id, rank, total_military_service_years
FROM personal
WHERE (rank = 'Lieutenant' AND total_military_service_years NOT BETWEEN 1 AND 3)
   OR (rank = 'Senior Lieutenant' AND total_military_service_years NOT BETWEEN 4 AND 6)
   OR (rank = 'Captain' AND total_military_service_years NOT BETWEEN 7 AND 11)
   OR (rank = 'Major' AND total_military_service_years NOT BETWEEN 12 AND 15)
   OR (rank = 'Lieutenant Colonel' AND total_military_service_years NOT BETWEEN 15 AND 30)
   OR (rank = 'Junior Warrant Officer' AND total_military_service_years NOT BETWEEN 1 AND 3)
   OR (rank = 'Warrant Officer' AND total_military_service_years NOT BETWEEN 3 AND 5)
   OR (rank = 'Senior Warrant Officer' AND total_military_service_years NOT BETWEEN 5 AND 20);


-- 6) TOP 10 HIGHEST-RISK PEOPLE (for a "watch list" dashboard)
SELECT r.person_id, r.department, r.rank, r.specialization, r.risk_score
FROM risk_score r
ORDER BY r.risk_score DESC
LIMIT 10;
