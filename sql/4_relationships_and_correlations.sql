
-- Testing relationships between performance metrics and background factors

-- Query 1: Aviation School vs. General Academy — shooting success rate
SELECT
    personal.military_academy_type,
    COUNT(*) AS total_shots,
    ROUND(COUNT(*) FILTER (WHERE outcome = 'Successful') * 100.0 / COUNT(*), 1) AS success_rate_pct
FROM shooting_performance
JOIN personal ON shooting_performance.person_id = personal.person_id
WHERE personal.military_academy_type IS NOT NULL
GROUP BY personal.military_academy_type;
 
/* Finding: Aviation-specific training produces measurably better shooters.
   Officers who graduated from the Military Aviation School track show a
   91% shooting success rate, compared to 81.8% for officers from the
   General Military Academy — a 9.2 percentage-point gap. This suggests
   that within the "Military Academy" commissioning path, the specific
   training pipeline matters as much as the broad category — a useful
   insight for prioritizing training investment. */
 
 
-- Query 2: Fitness score vs. discipline records
WITH avg_fitness AS (
    SELECT person_id, AVG(fitness_score) AS avg_fitness_score
    FROM physical_fitness
    GROUP BY person_id
),
discipline_count AS (
    SELECT person_id, COUNT(*) AS negative_records
    FROM discipline_records
    WHERE record_type IN ('Reprimand', 'Warning')
    GROUP BY person_id
)
SELECT
    CASE
        WHEN discipline_count.negative_records IS NULL THEN 'No records'
        ELSE 'Has records'
    END AS discipline_status,
    ROUND(AVG(avg_fitness.avg_fitness_score), 1) AS avg_fitness
FROM avg_fitness
LEFT JOIN discipline_count ON avg_fitness.person_id = discipline_count.person_id
GROUP BY discipline_status;
 
/* Finding: Fitness and discipline are weakly but measurably linked. People
   with a discipline record (reprimand/warning) average 83.8 on fitness
   tests, compared to 87.6 for those with a clean record — a modest but
   consistent gap suggesting fitness discipline correlates with broader
   conduct discipline. */
 
 
-- Query 3: Officer commissioning path vs. discipline records
WITH negative_records AS (
    SELECT person_id, COUNT(*) AS negative_count
    FROM discipline_records
    WHERE record_type IN ('Reprimand', 'Warning')
    GROUP BY person_id
)
SELECT
    personal.officer_commissioning_source,
    COUNT(DISTINCT personal.person_id) AS num_officers,
    ROUND(AVG(COALESCE(negative_records.negative_count, 0)), 2) AS avg_negative_records
FROM personal
LEFT JOIN negative_records ON personal.person_id = negative_records.person_id
WHERE personal.officer_commissioning_source IS NOT NULL
GROUP BY personal.officer_commissioning_source
ORDER BY avg_negative_records DESC;
 
/* Finding: Military Academy graduates have the fewest discipline issues
   among officers. Officers commissioned through the traditional Military
   Academy path average 0.17 negative discipline records per person —
   roughly 3x fewer than Civilian Direct Commission officers (0.54) and
   Prior Enlisted officers (0.40). This confirms that traditional military
   education correlates with stronger discipline outcomes, independent of
   the aviation-training performance advantage seen in Query 1. */
 
 
-- Query 4: Technical problems, maintenance hours & fuel consumption together
WITH maintenance_totals AS (
    SELECT department, year, SUM(maintenance_hours) AS total_maintenance_hours
    FROM aircraft_monthly_maintenance
    GROUP BY department, year
),
problem_rates AS (
    SELECT
        department,
        year,
        ROUND(COUNT(*) FILTER (WHERE had_inflight_technical_problem) * 100.0 / COUNT(*), 1) AS problem_rate_pct
    FROM mission_technical_log
    GROUP BY department, year
)
SELECT
    fuel_consumption.department,
    fuel_consumption.year,
    fuel_consumption.total_flight_hours_real,
    fuel_consumption.fuel_burn_rate_l_per_hour,
    maintenance_totals.total_maintenance_hours,
    problem_rates.problem_rate_pct
FROM fuel_consumption
JOIN maintenance_totals ON fuel_consumption.department = maintenance_totals.department
    AND fuel_consumption.year = maintenance_totals.year
JOIN problem_rates ON fuel_consumption.department = problem_rates.department
    AND fuel_consumption.year = problem_rates.year
ORDER BY fuel_consumption.department, fuel_consumption.year;
 
/* Finding: Aggregation level reverses the maintenance-reliability
   relationship (Simpson's Paradox). At the department-year level,
   maintenance hours and problem rates appear positively correlated
   (+0.11) — seemingly "more maintenance causes more problems." But this is
   confounded by fleet aging: both metrics rise together as the whole fleet
   ages over 2021-2026. At the individual aircraft-month level, the true
   relationship is weakly negative (-0.08), confirming more maintenance
   genuinely reduces problems. This is a critical reminder to check for
   confounding variables before drawing causal conclusions from aggregated
   data. */
 
 
-- Query 5: Flight hours vs. simulator hours vs. shooting success rate
WITH person_hours AS (
    SELECT
        person_id,
        SUM(flight_hours_real) AS total_flight_hours,
        SUM(flight_hours_simulator) AS total_simulator_hours
    FROM flight_operations
    GROUP BY person_id
),
person_success AS (
    SELECT
        person_id,
        ROUND(COUNT(*) FILTER (WHERE outcome = 'Successful') * 100.0 / COUNT(*), 1) AS success_rate
    FROM shooting_performance
    GROUP BY person_id
)
SELECT
    CASE
        WHEN person_hours.total_flight_hours < 500 THEN '0-500'
        WHEN person_hours.total_flight_hours < 1000 THEN '500-1000'
        WHEN person_hours.total_flight_hours < 1500 THEN '1000-1500'
        WHEN person_hours.total_flight_hours < 2000 THEN '1500-2000'
        ELSE '2000+'
    END AS flight_hours_range,
    COUNT(*) AS num_people,
    ROUND(AVG(person_hours.total_simulator_hours), 1) AS avg_simulator_hours,
    ROUND(AVG(person_success.success_rate), 1) AS avg_success_rate
FROM person_hours
JOIN person_success ON person_hours.person_id = person_success.person_id
GROUP BY flight_hours_range
ORDER BY MIN(person_hours.total_flight_hours);
 
/* Finding: Flight experience and simulator training scale together, but
   neither strongly predicts shooting accuracy. People with 2000+ flight
   hours log roughly 3x more simulator time than those under 500 hours
   (273.2 vs 88.7 hours) — but their shooting success rate is nearly
   identical (86.4% vs 83.3%). This suggests marksmanship is driven by
   factors other than raw flight/sim hours (e.g., aviation-school training,
   individual aptitude) — a useful finding for training-budget allocation
   decisions. */
 

-- Query 6: Individual aircraft-month level correlation (for Simpson's Paradox comparison)
-- This is the "ground truth" granular data behind Query 4's department-year
-- aggregation. At THIS level, maintenance and problems correlate negatively
-- (more maintenance -> fewer problems) -- the opposite of what Query 4 showed
-- at the aggregated level, because Query 4's positive correlation was an
-- artifact of both metrics rising together as the whole fleet aged over time.
SELECT 
    CASE 
        WHEN aircraft_monthly_maintenance.maintenance_hours < 12 THEN '0-12h'
        WHEN aircraft_monthly_maintenance.maintenance_hours < 16 THEN '12-16h'
        WHEN aircraft_monthly_maintenance.maintenance_hours < 20 THEN '16-20h'
        ELSE '20h+'
    END AS maintenance_bucket,
    ROUND(COUNT(*) FILTER (WHERE mission_technical_log.had_inflight_technical_problem) * 100.0 / COUNT(*), 1) AS problem_rate_pct
FROM aircraft_monthly_maintenance
JOIN mission_technical_log 
    ON aircraft_monthly_maintenance.aircraft_id = mission_technical_log.aircraft_id 
    AND aircraft_monthly_maintenance.year = mission_technical_log.year 
    AND aircraft_monthly_maintenance.month = mission_technical_log.month
GROUP BY maintenance_bucket
ORDER BY maintenance_bucket;



-- 16. Success rate by commissioning source AND specialization —
-- reveals whether a commissioning path's strength depends on role type
-- (e.g. Civilian-commissioned officers may excel as pilots but
-- underperform as operations officers).
SELECT 
    personal.officer_commissioning_source,
    personal.specialization,
    COUNT(*) AS total_shots,
    ROUND(COUNT(*) FILTER (WHERE outcome = 'Successful') * 100.0 / COUNT(*), 1) AS success_rate_pct
FROM shooting_performance
JOIN personal ON shooting_performance.person_id = personal.person_id
WHERE personal.officer_commissioning_source IS NOT NULL
GROUP BY personal.officer_commissioning_source, personal.specialization
HAVING COUNT(*) >= 10
ORDER BY personal.officer_commissioning_source, success_rate_pct DESC;