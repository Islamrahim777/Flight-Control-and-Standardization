--1. How many people are in each department? (personal, GROUP BY department) //
select department, count(*) as num_people 
from personal
group by department
order by department asc;

--2 . How many officers vs. warrant officers are there? (by rank_group)
select rank_group, count(*) as num_people
from personal
group by rank_group
order by rank_group asc;


-- 3. Who is the youngest and oldest person?
(
select first_name, last_name, age as youngest
    from personal
    order by youngest asc
limit 1
)
Union ALL
(
select  
    first_name,
    last_name, 
    age as oldest
from personal
order by oldest desc
limit 1
);
 

 -- 4. Birthday Queries
 select 
    first_name,
    last_name, 
    extract(month from birth_date) as month,
    extract(day from birth_date) as day
from personal
group by first_name, last_name,month, day
order by month asc, day ASC

 -- 5. Birthday Distribution by Month

select 
    to_char(birth_date, 'Month') as Months,
    count(*) as num_birthdays
from personal
group by months 
order by months asc;

-- 6.Age Distribution Across the Unit

select 
    age,
    count(*) as num_people
from personal
group by age
order by age asc;

-- 7. Headcount by Rank, Ordered by Seniority (Junior -> Senior
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