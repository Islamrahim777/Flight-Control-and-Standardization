/* Finding: Reward system inequity is concentrated in Sigma department. 
    Among the 17 personnel who combine elite performance (≥90% shooting success rate, ≥800 total flight hours) with minimal recognition (fewer than 2 medals), 29% (5 of 17) belong to Sigma — the highest concentration of any department, despite Sigma having the same headcount as its peers. 
    This aligns with Sigma's pattern in other metrics (lowest technical reliability score, weakest fuel efficiency), suggesting the department may have a broader leadership/recognition culture issue rather than an isolated anomaly. */


-- Total cumulative flight hours by rank (all years combined)
-- Average cumulative flight hours by rank, ordered by seniority (senior -> junior)
-- Average LAST-12-MONTH total flight hours per person, by rank
WITH person_totals AS (
    SELECT 
        flight_operations.person_id,
        SUM(flight_operations.flight_hours_real) AS total_last_12mo
    FROM flight_operations
    WHERE (year = 2025 AND month > 6) OR (year = 2026 AND month <= 6)
    GROUP BY flight_operations.person_id
)
SELECT 
    personal.rank,
    ROUND(AVG(person_totals.total_last_12mo), 1) AS avg_last_12mo_hours
FROM personal
JOIN person_totals ON personal.person_id = person_totals.person_id
GROUP BY personal.rank
ORDER BY 
    CASE personal.rank
        WHEN 'Lieutenant Colonel' THEN 7 WHEN 'Major' THEN 6 WHEN 'Captain' THEN 5
        WHEN 'Senior Lieutenant' THEN 4 WHEN 'Lieutenant' THEN 3
        WHEN 'Senior Warrant Officer' THEN 2 WHEN 'Warrant Officer' THEN 1
        WHEN 'Junior Warrant Officer' THEN 0
    END DESC;


  WITH success_rates AS (
    SELECT person_id, COUNT(*) FILTER (WHERE outcome = 'Successful') * 100.0 / COUNT(*) AS success_rate
    FROM shooting_performance
    GROUP BY person_id
),
flight_totals AS (
    SELECT person_id, SUM(flight_hours_real) AS total_hours
    FROM flight_operations
    GROUP BY person_id
),
medal_counts AS (
    SELECT person_id, COUNT(*) AS medal_count
    FROM medals
    GROUP BY person_id
)
SELECT 
    personal.department,
    COUNT(*) AS underrecognized_people
FROM personal
JOIN success_rates ON personal.person_id = success_rates.person_id
JOIN flight_totals ON personal.person_id = flight_totals.person_id
LEFT JOIN medal_counts ON personal.person_id = medal_counts.person_id
WHERE success_rates.success_rate >= 90
  AND flight_totals.total_hours >= 800
  AND COALESCE(medal_counts.medal_count, 0) < 2
GROUP BY personal.department
ORDER BY underrecognized_people DESC;



    SELECT 
    department,
    COUNT(*) FILTER (WHERE record_type IN ('Reprimand', 'Warning')) AS negative_records,
    COUNT(*) FILTER (WHERE record_type = 'Commendation') AS positive_records
FROM discipline_records
GROUP BY department
ORDER BY negative_records DESC;

SELECT department, ROUND(AVG(risk_score), 1) AS avg_risk_score
FROM risk_score
GROUP BY department
ORDER BY avg_risk_score DESC;

Finding: Sigma's weaknesses are structural, not behavioral. Despite having the lowest technical reliability score and the highest share of under-recognized top performers, Sigma actually has the fewest discipline problems (25 negative records) of all 5 departments — Alpha has the most (36). This suggests Sigma's issues stem from equipment/leadership recognition gaps, not personnel misconduct — an important distinction for any intervention plan (fixing Sigma requires investment in aircraft maintenance and a fairer reward process, not disciplinary reform).

RISK BALI

SELECT department, ROUND(AVG(risk_score), 1) AS avg_risk_score
FROM risk_score
GROUP BY department
ORDER BY avg_risk_score DESC;


ATIS

SELECT is_first_shot, COUNT(*) AS total_shots,
    ROUND(COUNT(*) FILTER (WHERE outcome = 'Successful') * 100.0 / COUNT(*), 1) AS success_rate_pct
FROM shooting_performance
GROUP BY is_first_shot;

TEXNIKI

SELECT aircraft_age_years,
    ROUND(COUNT(*) FILTER (WHERE had_inflight_technical_problem) * 100.0 / COUNT(*), 1) AS problem_rate_pct
FROM mission_technical_log
GROUP BY aircraft_age_years
ORDER BY aircraft_age_years ASC;