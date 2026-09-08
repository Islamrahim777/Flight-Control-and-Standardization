"""
Generates:
  - fitness_standards.csv

Detailed age-graded PT scoring chart: for each age group and each score
band (10,20,...,100), the exact pull-up count and 3km-run time required.

Base standard (age group 1, 18-25): 18 pull-ups = 100 pts, 13:00 min run
= 100 pts, passing score = 60 pts. Each 10-point band steps by 2
pull-ups / 1 minute. Each subsequent age group gets a 1-pull-up /
0.5-minute concession at every band (relaxes with age).

Run: python3 generate_fitness_standards.py
"""

import pandas as pd

BASE_PULLUP_100PT = 18
PULLUP_STEP_PER_10PTS = 2
PULLUP_CONCESSION_PER_GROUP = 1        # fewer pull-ups required per older group

BASE_RUN_100PT = 13.0                   # minutes
RUN_STEP_PER_10PTS = 1.0                # minutes
RUN_CONCESSION_PER_GROUP = 0.5          # more time allowed per older group

AGE_GROUPS = [(1, "18-25"), (2, "26-30"), (3, "31-35"), (4, "36-40"), (5, "41+")]
SCORES = list(range(100, 0, -10))       # 100, 90, ..., 10
PASSING_SCORE = 60


def main():
    rows = []
    for group, age_range in AGE_GROUPS:
        pullup_100 = BASE_PULLUP_100PT - (group - 1) * PULLUP_CONCESSION_PER_GROUP
        run_100 = BASE_RUN_100PT + (group - 1) * RUN_CONCESSION_PER_GROUP
        for score in SCORES:
            steps_below_100 = (100 - score) / 10
            pullups_required = max(0, round(pullup_100 - steps_below_100 * PULLUP_STEP_PER_10PTS))
            run_minutes_required = round(run_100 + steps_below_100 * RUN_STEP_PER_10PTS, 1)
            rows.append({
                "age_group": group,
                "age_range": age_range,
                "score": score,
                "pullups_required": pullups_required,
                "run_minutes_required": run_minutes_required,
                "is_passing": score >= PASSING_SCORE,
            })

    df = pd.DataFrame(rows)
    df.to_csv("/home/claude/fitness_standards.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()

