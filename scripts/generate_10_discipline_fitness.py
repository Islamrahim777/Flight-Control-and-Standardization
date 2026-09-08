"""
Generates:
  - physical_fitness.csv     (annual fitness test, ALL personnel)
  - discipline_records.csv   (sparse reprimand/commendation log)

Discipline risk is only SOFTLY linked to fitness score and tactical
training participation (weak, noisy relationship — same philosophy as
the rest of this dataset), which is what the user wants to investigate:
"is discipline related to courses and sports results?"

Depends on personal.csv, tactical_training.csv.
Run: python3 generate_10_discipline_fitness.py
"""

import random
import numpy as np
import pandas as pd

from uav_dataset_config import REFERENCE_DATE

random.seed(50)
np.random.seed(50)

YEARS = [2021, 2022, 2023, 2024, 2025, 2026]

RECORD_TYPES = ["Reprimand", "Warning", "Commendation"]
REPRIMAND_REASONS = ["Late Arrival", "Uniform/Regulation Violation",
                      "Unauthorized Absence", "Insubordination", "Equipment Mishandling"]
COMMENDATION_REASONS = ["Exemplary Conduct", "Outstanding Duty Performance"]


OFFICER_LEVEL = {"Lieutenant": 0, "Senior Lieutenant": 1, "Captain": 2, "Major": 3, "Lieutenant Colonel": 4}
WARRANT_LEVEL = {"Junior Warrant Officer": 0, "Warrant Officer": 1, "Senior Warrant Officer": 2}


def load_standards():
    detailed = pd.read_csv("/home/claude/fitness_standards.csv")
    # Build simple per-group anchors (score=10 floor, score=100 ceiling) from
    # the detailed chart, so the interpolation formula matches it exactly.
    anchors = {}
    for g, grp in detailed.groupby("age_group"):
        lo = grp[grp.score == 10].iloc[0]
        hi = grp[grp.score == 100].iloc[0]
        anchors[g] = {
            "pullups_for_10pt": lo["pullups_required"], "pullups_for_100pt": hi["pullups_required"],
            "run_minutes_for_10pt": lo["run_minutes_required"], "run_minutes_for_100pt": hi["run_minutes_required"],
        }
    return pd.DataFrame(anchors).T


def age_group(age: int) -> int:
    if age <= 25:
        return 1
    if age <= 30:
        return 2
    if age <= 35:
        return 3
    if age <= 40:
        return 4
    return 5


def score_from_standard(value, lo_for_0pt, hi_for_100pt):
    """Linear interpolation between the 10-point and 100-point thresholds
    (minimum score floor is 10, not 0 — everyone gets at least 10 points)."""
    if hi_for_100pt == lo_for_0pt:
        return 100.0
    pct = (value - lo_for_0pt) / (hi_for_100pt - lo_for_0pt) * 90 + 10
    return float(max(10.0, min(100.0, pct)))


def main():
    personal_df = pd.read_csv("/home/claude/personal.csv")
    tactical_df = pd.read_csv("/home/claude/tactical_training.csv")
    standards = load_standards()

    trainings_per_person = tactical_df.groupby("person_id").size()

    # ---------------- Physical fitness (annual, everyone) -----------------
    # Two raw components: pull-ups (turnik) and 3km run time (qaçış).
    #   - Officers: strong when young/junior, DECLINE as rank rises.
    #   - Civilian-commissioned officers: relatively weak specifically at
    #     pull-ups (upper-body strength), per user rule.
    #   - Gizirs: fitness is roughly "normal" overall, but specifically
    #     IMPROVES with seniority (senior/veteran gizirs are the fittest —
    #     conditioning built up over years of service), opposite direction
    #     from the officer pattern.
    fitness_rows = []
    for _, r in personal_df.iterrows():
        join_year = max(2021, int(REFERENCE_DATE.year - r["uav_service_years"]))
        commissioning = r.get("officer_commissioning_source")
        is_officer = r["rank_group"] == "Officer"

        if is_officer:
            rank_level = OFFICER_LEVEL[r["rank"]]
            base_pullups = 16 - rank_level * 1.8
            base_run = 13.0 + rank_level * 0.4
            if commissioning == "Civilian Direct Commission":
                base_pullups -= 4  # weaker specifically at pull-ups
        else:
            rank_level = WARRANT_LEVEL[r["rank"]]
            base_pullups = 10 + rank_level * 3.0   # improves with seniority
            base_run = 15.0 - rank_level * 0.8      # faster (lower) with seniority

        for year in YEARS:
            if year < join_year:
                continue
            age_that_year = r["age"] - (REFERENCE_DATE.year - year)
            age_penalty = max(0, (age_that_year - 35) * 0.3)  # small extra effect for very senior ages

            if is_officer:
                pullups = float(np.clip(np.random.normal(base_pullups - age_penalty * 0.3, 3), 0, 30))
                run_time = float(np.clip(np.random.normal(base_run + age_penalty * 0.05, 1.6), 9, 20))
            else:
                # Gizirs: peak in middle age (~38) on top of the seniority effect,
                # rather than a simple monotonic age decline.
                mid_age_effect = 8 - abs(age_that_year - 38) * 0.3
                pullups = float(np.clip(np.random.normal(base_pullups + mid_age_effect, 3), 0, 30))
                run_time = float(np.clip(np.random.normal(base_run - mid_age_effect * 0.06, 1.6), 9, 20))

            pullups_rounded = round(pullups)
            run_rounded = round(run_time, 2)

            # Age-adjusted scoring: look up this person's age-group standard
            # and interpolate their raw performance against it.
            ag = age_group(age_that_year)
            row_std = standards.loc[ag]
            pullup_score = round(score_from_standard(
                pullups_rounded, row_std["pullups_for_10pt"], row_std["pullups_for_100pt"]), 1)
            # Run time is inverted: LOWER time is better, so 10pt threshold is
            # the SLOWER (higher-minutes) bound and 100pt is the FASTER bound.
            run_score = round(score_from_standard(
                -run_rounded, -row_std["run_minutes_for_10pt"], -row_std["run_minutes_for_100pt"]), 1)
            score = round(0.5 * pullup_score + 0.5 * run_score + 1e-9, 1)

            fitness_rows.append({
                "person_id": r["person_id"],
                "year": year,
                "age_group": ag,
                "pullups_count": pullups_rounded,
                "run_3km_minutes": run_rounded,
                "pullup_score": pullup_score,
                "run_score": run_score,
                "fitness_score": score,
                "result": "Pass" if score >= 60 else "Fail",
            })
    fitness_df = pd.DataFrame(fitness_rows)
    avg_fitness = fitness_df.groupby("person_id")["fitness_score"].mean()

    # ---------------- Discipline records (sparse) --------------------------
    disc_rows = []
    rec_counter = 1
    for _, r in personal_df.iterrows():
        pid = r["person_id"]
        fit = avg_fitness.get(pid, 75)
        n_train = trainings_per_person.get(pid, 0)

        # Softly higher reprimand propensity for lower fitness / fewer trainings
        # (continuous, not just a threshold effect, so a mild real relationship
        # actually shows up in the aggregate stats — but noise still dominates).
        # NOTE: threshold recalibrated to the current fitness scale (mean ~87).
        propensity = 0.20 + max(0, (90 - fit)) * 0.018 + max(0, (2 - n_train)) * 0.03

        commissioning = r.get("officer_commissioning_source")
        if commissioning == "Military Academy":
            propensity -= 0.08
        elif commissioning == "Civilian Direct Commission":
            propensity += 0.10
        elif commissioning == "Prior Enlisted (Gizir) Commission":
            propensity += 0.12
        lam_neg = float(np.clip(propensity, 0.05, 0.55))
        n_negative = np.random.poisson(lam_neg)
        n_negative = min(n_negative, 3)

        n_positive = np.random.poisson(0.15)
        n_positive = min(n_positive, 2)

        join_year = max(2021, int(REFERENCE_DATE.year - r["uav_service_years"]))
        for _ in range(n_negative):
            year = random.randint(join_year, REFERENCE_DATE.year)
            month = random.randint(1, 12 if year < REFERENCE_DATE.year else REFERENCE_DATE.month)
            rtype = random.choices(["Reprimand", "Warning"], weights=[0.4, 0.6])[0]
            disc_rows.append({
                "record_id": f"D{rec_counter:04d}", "person_id": pid, "department": r["department"],
                "year": year, "month": month, "record_type": rtype,
                "severity": "Major" if rtype == "Reprimand" and random.random() < 0.25 else "Minor",
                "reason": random.choice(REPRIMAND_REASONS),
            })
            rec_counter += 1
        for _ in range(n_positive):
            year = random.randint(join_year, REFERENCE_DATE.year)
            month = random.randint(1, 12 if year < REFERENCE_DATE.year else REFERENCE_DATE.month)
            disc_rows.append({
                "record_id": f"D{rec_counter:04d}", "person_id": pid, "department": r["department"],
                "year": year, "month": month, "record_type": "Commendation",
                "severity": None, "reason": random.choice(COMMENDATION_REASONS),
            })
            rec_counter += 1

    discipline_df = pd.DataFrame(disc_rows)

    fitness_df.to_csv("/home/claude/physical_fitness.csv", index=False)
    discipline_df.to_csv("/home/claude/discipline_records.csv", index=False)

    print(f"Fitness rows: {len(fitness_df)}  (Pass rate: {(fitness_df.result=='Pass').mean():.1%})")
    print()
    print(f"Discipline rows: {len(discipline_df)}")
    print(discipline_df.record_type.value_counts())
    print()
    print("Sanity check — avg fitness score for people w/ vs w/o negative records:")
    neg_people = set(discipline_df[discipline_df.record_type.isin(["Reprimand", "Warning"])].person_id)
    print("With negative record:", avg_fitness[avg_fitness.index.isin(neg_people)].mean().round(1))
    print("Without:", avg_fitness[~avg_fitness.index.isin(neg_people)].mean().round(1))


if __name__ == "__main__":
    main()
