
-- Year/month/department breakdowns for operational metrics

-- 1. Flight hours by department + year
SELECT department, year, round(SUM(flight_hours_real),0) AS total_flight_hours
FROM flight_operations
GROUP BY department, year
ORDER BY department, year;
 
-- 2. Shooting performance by department + year + month
SELECT
    department,
    EXTRACT(YEAR FROM shot_date) AS year,
    EXTRACT(MONTH FROM shot_date) AS month,
    COUNT(*) AS total_shots,
    ROUND(COUNT(*) FILTER (WHERE outcome = 'Successful') * 100.0 / COUNT(*), 1) AS success_rate_pct
FROM shooting_performance
GROUP BY department, year, month
ORDER BY department, year, month;
 
-- 3. Standardization exam pass rate by department + year
-- (No month breakdown possible — this exam is administered once per year)
SELECT
    department,
    exam_year,
    COUNT(*) AS total_exams,
    ROUND(COUNT(*) FILTER (WHERE final_clearance_status = 'Cleared') * 100.0 / COUNT(*), 1) AS pass_rate_pct
FROM standardization_exams
GROUP BY department, exam_year
ORDER BY department, exam_year;
 
-- 4. Discipline penalties by department + year + month
SELECT
    department,
    year,
    month,
    COUNT(*) FILTER (WHERE record_type IN ('Reprimand', 'Warning')) AS penalty_count
FROM discipline_records
GROUP BY department, year, month
ORDER BY department, year, month;
 
-- 5. Discipline penalties by department + year (annual summary, no month)
SELECT
    department,
    year,
    COUNT(*) FILTER (WHERE record_type IN ('Reprimand', 'Warning')) AS penalty_count
FROM discipline_records
GROUP BY department, year
ORDER BY department, year;
 
-- 6. Simulator hours by department + year + month
SELECT department, year, month, SUM(flight_hours_simulator) AS total_simulator_hours
FROM flight_operations
GROUP BY department, year, month
ORDER BY department, year, month;
 
-- 7. Technical problems by department + year + month
SELECT
    department,
    year,
    month,
    COUNT(*) FILTER (WHERE had_inflight_technical_problem) AS technical_problem_count,
    COUNT(*) AS total_missions
FROM mission_technical_log
GROUP BY department, year, month
ORDER BY department, year, month;
 
-- 8. Mission volume by weather condition (unit-wide, all years)
SELECT
    dominant_weather,
    COUNT(*) AS total_missions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_all_missions
FROM mission_log
GROUP BY dominant_weather
ORDER BY total_missions DESC;
 
-- 9. Mission volume by calendar month (unit-wide, all years combined)
-- Used for operational planning: training/leave scheduling should account
-- for this seasonal demand pattern.
SELECT month, COUNT(*) AS total_missions
FROM mission_log
GROUP BY month
ORDER BY month;
 
/* Finding: Mission demand is strongly seasonal. May is the peak month
   (7,375 missions) and December the quietest (2,552) — roughly a 2.9x
   difference. The unit should concentrate personnel leave/vacation in the
   December-February low-demand window and minimize leave approvals during
   the May-August peak, when full staffing is most operationally needed. */


-- 10. Annual flight hours per person (2025) — for annual minimum requirement tracking
 SELECT 
    personal.person_id,
    personal.first_name,
    personal.last_name,
    personal.department,
    personal.rank,
    SUM(flight_operations.flight_hours_real) AS annual_flight_hours
FROM personal
JOIN flight_operations ON personal.person_id = flight_operations.person_id
WHERE flight_operations.year = 2025
GROUP BY personal.person_id, personal.first_name, personal.last_name, personal.department, personal.rank
ORDER BY annual_flight_hours ASC; 


-- 10. Combined monthly operations metrics (flight hours, estimated fuel,
-- shooting activity, technical problems) — for interactive Tableau
-- dashboard filtered by Year + Month.
WITH monthly_flight AS (
    SELECT department, year, month, SUM(flight_hours_real) AS total_flight_hours
    FROM flight_operations
    GROUP BY department, year, month
),
monthly_shots AS (
    SELECT
        department,
        EXTRACT(YEAR FROM shot_date) AS year,
        EXTRACT(MONTH FROM shot_date) AS month,
        COUNT(*) AS total_shots
    FROM shooting_performance
    GROUP BY department, EXTRACT(YEAR FROM shot_date), EXTRACT(MONTH FROM shot_date)
),
monthly_problems AS (
    SELECT department, year, month, COUNT(*) FILTER (WHERE had_inflight_technical_problem) AS technical_problem_count
    FROM mission_technical_log
    GROUP BY department, year, month
)
SELECT
    monthly_flight.department,
    monthly_flight.year,
    monthly_flight.month,
    monthly_flight.total_flight_hours,
    ROUND(monthly_flight.total_flight_hours * fuel_consumption.fuel_burn_rate_l_per_hour) AS estimated_fuel_liters,
    COALESCE(monthly_shots.total_shots, 0) AS total_shots,
    COALESCE(monthly_problems.technical_problem_count, 0) AS technical_problem_count
FROM monthly_flight
LEFT JOIN fuel_consumption
    ON fuel_consumption.department = monthly_flight.department
    AND fuel_consumption.year = monthly_flight.year
LEFT JOIN monthly_shots
    ON monthly_shots.department = monthly_flight.department
    AND monthly_shots.year = monthly_flight.year
    AND monthly_shots.month = monthly_flight.month
LEFT JOIN monthly_problems
    ON monthly_problems.department = monthly_flight.department
    AND monthly_problems.year = monthly_flight.year
    AND monthly_problems.month = monthly_flight.month
ORDER BY monthly_flight.department, monthly_flight.year, monthly_flight.month;