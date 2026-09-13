-- UNION / INTERSECT / EXCEPT and multi-level aggregation (ROLLUP,
-- GROUPING SETS) — combining and slicing result sets in ways that
-- plain GROUP BY / WHERE cannot.

-- Setup context: "top flyers" = person total flight hours >= 1500
--                "top shooters" = person shooting success rate >= 90%
 
-- Query 1: UNION — everyone who is EITHER a top flyer OR a top shooter
-- (UNION removes duplicates automatically — someone who is both only
--  appears once. Use UNION ALL instead if you want duplicates kept.)
WITH top_flyers AS (
    SELECT person_id FROM flight_operations
    GROUP BY person_id HAVING SUM(flight_hours_real) >= 1500
),
top_shooters AS (
    SELECT person_id FROM shooting_performance
    GROUP BY person_id HAVING COUNT(*) FILTER (WHERE outcome = 'Successful') * 100.0 / COUNT(*) >= 90
)
SELECT person_id FROM top_flyers
UNION
SELECT person_id FROM top_shooters;
-- Expect 122 people total
 
 
-- Query 2: INTERSECT — people who are BOTH a top flyer AND a top shooter
WITH top_flyers AS (
    SELECT person_id FROM flight_operations
    GROUP BY person_id HAVING SUM(flight_hours_real) >= 1500
),
top_shooters AS (
    SELECT person_id FROM shooting_performance
    GROUP BY person_id HAVING COUNT(*) FILTER (WHERE outcome = 'Successful') * 100.0 / COUNT(*) >= 90
)
SELECT person_id FROM top_flyers
INTERSECT
SELECT person_id FROM top_shooters;
-- Expect 16 people — the true "elite on both fronts" group
 
 
-- Query 3: EXCEPT — top flyers who are NOT also top shooters
-- (Order matters with EXCEPT: "A EXCEPT B" = rows in A but not in B)
WITH top_flyers AS (
    SELECT person_id FROM flight_operations
    GROUP BY person_id HAVING SUM(flight_hours_real) >= 1500
),
top_shooters AS (
    SELECT person_id FROM shooting_performance
    GROUP BY person_id HAVING COUNT(*) FILTER (WHERE outcome = 'Successful') * 100.0 / COUNT(*) >= 90
)
SELECT person_id FROM top_flyers
EXCEPT
SELECT person_id FROM top_shooters;
-- Expect 30 people — lots of flight time, but not elite marksmanship
 
/* Finding: Flight experience and shooting excellence are largely separate
   skill sets. Of 46 top flyers (>=1500 hrs) and 92 top shooters (>=90%
   success), only 16 people qualify as both — most top flyers (30 of 46)
   do not also rank as top shooters. This reinforces the earlier finding
   that raw flight hours are a weak predictor of marksmanship, and argues
   for evaluating and rewarding these as two distinct competencies rather
   than assuming one implies the other. */
 
 
-- Query 4: ROLLUP — department subtotals AND a grand total, in one query
-- (Without ROLLUP this would need a GROUP BY query plus a separate
--  no-GROUP-BY query, UNIONed together by hand.)
SELECT
    COALESCE(department, 'ALL DEPARTMENTS') AS department,
    COUNT(*) AS num_people
FROM personal
GROUP BY ROLLUP(department)
ORDER BY department;
 
 
-- Query 5: GROUPING SETS — headcount by department, by rank_group, AND
-- overall — three different levels of aggregation in a single result set
SELECT
    COALESCE(department, 'ALL') AS department,
    COALESCE(rank_group, 'ALL') AS rank_group,
    COUNT(*) AS num_people
FROM personal
GROUP BY GROUPING SETS ((department), (rank_group), ())
ORDER BY department, rank_group;
 
