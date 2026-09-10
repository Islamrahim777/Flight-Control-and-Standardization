
/














1 basic queries · SQL
-- ============================================================
-- 1_basic_queries.sql
-- Basic descriptive statistics on the UAV unit personnel
-- ============================================================
 
-- 1. How many people are in each department?
SELECT department, COUNT(*) AS num_people
FROM personal
GROUP BY department
ORDER BY department ASC;
 
-- 2. How many officers vs. warrant officers are there?
SELECT rank_group, COUNT(*) AS num_people
FROM personal
GROUP BY rank_group
ORDER BY rank_group ASC;
 
-- 3. Who is the youngest and oldest person? (exact birth_date, one row each)
(SELECT first_name, last_name, birth_date, 'youngest' AS category
 FROM personal ORDER BY birth_date DESC LIMIT 1)
UNION ALL
(SELECT first_name, last_name, birth_date, 'oldest' AS category
 FROM personal ORDER BY birth_date ASC LIMIT 1);
 
-- 4. Everyone's birthday (day + month), sorted by calendar order
SELECT
    first_name,
    last_name,
    EXTRACT(MONTH FROM birth_date) AS birth_month,
    EXTRACT(DAY FROM birth_date) AS birth_day
FROM personal
ORDER BY birth_month ASC, birth_day ASC;
 
-- 5. Birthday distribution by month (headcount per month, calendar order)
SELECT
    TO_CHAR(birth_date, 'Month') AS month_name,
    COUNT(*) AS num_birthdays
FROM personal
GROUP BY month_name, EXTRACT(MONTH FROM birth_date)
ORDER BY EXTRACT(MONTH FROM birth_date) ASC;
 
-- 6. Age distribution across the unit
SELECT age, COUNT(*) AS num_people
FROM personal
GROUP BY age
ORDER BY age ASC;
 
-- 7. Headcount by rank, ordered by seniority (junior -> senior)
SELECT
    rank,
    COUNT(*) AS num_people,
    CASE rank
        WHEN 'Junior Warrant Officer' THEN 0
        WHEN 'Warrant Officer' THEN 1
        WHEN 'Senior Warrant Officer' THEN 2
        WHEN 'Lieutenant' THEN 3
        WHEN 'Senior Lieutenant' THEN 4
        WHEN 'Captain' THEN 5
        WHEN 'Major' THEN 6
        WHEN 'Lieutenant Colonel' THEN 7
    END AS seniority_order
FROM personal
GROUP BY rank
ORDER BY seniority_order ASC;
 
-- 8. Driving license rate (% of people who have one)
SELECT
    ROUND(SUM(CASE WHEN has_driving_license THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1)
        AS driving_license_rate_pct
FROM personal;
 
-- 9. Language certification rate by department (% of the 3-certificate max)
SELECT
    personal.department,
    ROUND(SUM(
        CASE WHEN english_certified THEN 1 ELSE 0 END +
        CASE WHEN russian_certified THEN 1 ELSE 0 END +
        CASE WHEN other_language_certified THEN 1 ELSE 0 END
    ) * 100.0 / (COUNT(*) * 3), 1) AS avg_certification_pct
FROM certifications
JOIN personal ON personal.person_id = certifications.person_id
GROUP BY personal.department
ORDER BY avg_certification_pct DESC;
 
-- 10. Language certification rate by rank_group (same measure as #9)
SELECT
    personal.rank_group,
    ROUND(SUM(
        CASE WHEN english_certified THEN 1 ELSE 0 END +
        CASE WHEN russian_certified THEN 1 ELSE 0 END +
        CASE WHEN other_language_certified THEN 1 ELSE 0 END
    ) * 100.0 / (COUNT(*) * 3), 1) AS avg_certification_pct
FROM certifications
JOIN personal ON personal.person_id = certifications.person_id
GROUP BY personal.rank_group
ORDER BY avg_certification_pct DESC;
 
-- 11. % of people with AT LEAST ONE language certification
SELECT
    ROUND(COUNT(*) FILTER (
        WHERE english_certified OR russian_certified OR other_language_certified
    ) * 100.0 / COUNT(*), 1) AS at_least_one_cert_pct
FROM certifications
JOIN personal ON certifications.person_id = personal.person_id;
 
-- 12. Education level breakdown
SELECT education_level, COUNT(*) AS person_count
FROM personal
GROUP BY education_level
ORDER BY person_count DESC;
 
