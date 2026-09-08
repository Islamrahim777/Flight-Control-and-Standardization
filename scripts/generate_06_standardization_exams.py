"""
Generates:
  - standardization_exams.csv   (Table 7: Standardlaşdırma/imtahanlar)
    One row per flight-eligible person per year they were active.

Depends on personal.csv and flight_operations.csv (to know who's
flight-eligible and which years they were active).
Run: python3 generate_06_standardization_exams.py
"""

import random
import numpy as np
import pandas as pd

random.seed(47)
np.random.seed(47)

PASS_THRESHOLD = 70

OFFICER_LEVEL = {"Lieutenant": 0, "Senior Lieutenant": 1, "Captain": 2,
                 "Major": 3, "Lieutenant Colonel": 4}
WARRANT_LEVEL = {"Junior Warrant Officer": 0, "Warrant Officer": 1, "Senior Warrant Officer": 2}

FEATURED_TOP_PERFORMERS = {"AO17018", "AO16543"}


def rank_level(rank_group, rank):
    return OFFICER_LEVEL[rank] if rank_group == "Officer" else WARRANT_LEVEL[rank]


def exam_bonus(pid, row, lang_bonus_ids, delayed_ids):
    spec = row["specialization"]
    commissioning = row.get("officer_commissioning_source")
    academy_type = row.get("military_academy_type")

    bonus = 0.0
    if pid in FEATURED_TOP_PERFORMERS:
        bonus += 8
    if commissioning == "Military Academy" and spec in ("Operations Officer", "Department Commander"):
        bonus += 6  # military-academy command track: strongest exam performers
    if academy_type == "Military Aviation School":
        bonus += 4
    if pid in lang_bonus_ids:
        bonus += 2
    if pid in delayed_ids:
        bonus -= 10
    return bonus


def main():
    personal_df = pd.read_csv("/home/claude/personal.csv")
    flight_df = pd.read_csv("/home/claude/flight_operations.csv")
    certs_df = pd.read_csv("/home/claude/certifications.csv")
    delay_df = pd.read_csv("/home/claude/rank_delay_analysis.csv")

    lang_bonus_ids = set(certs_df[(certs_df.english_certified == True)
                                   | (certs_df.other_language_certified == True)].person_id)
    delayed_ids = set(delay_df[delay_df.rank_delayed == True].person_id)

    # Which (person_id, year) combinations are active flight-eligible periods
    active_years = flight_df[["person_id", "department", "year"]].drop_duplicates()

    # Each department's designated evaluator = its Training & Standardization Lead
    dept_evaluator = (personal_df[personal_df.specialization == "Training & Standardization Lead"]
                       .set_index("department")["person_id"].to_dict())
    dept_commander = (personal_df[personal_df.specialization == "Department Commander"]
                       .set_index("department")["person_id"].to_dict())

    personal_lookup = personal_df.set_index("person_id")

    rows = []
    for _, r in active_years.iterrows():
        pid, dept, year = r["person_id"], r["department"], int(r["year"])
        prow = personal_lookup.loc[pid]
        lvl = rank_level(prow["rank_group"], prow["rank"])

        base = 75 + lvl * 1.5 + exam_bonus(pid, prow, lang_bonus_ids, delayed_ids)
        score = float(np.clip(np.random.normal(base, 10), 35, 100))
        score = round(score, 1)

        cleared_first_try = score >= PASS_THRESHOLD
        retake_required = not cleared_first_try
        if retake_required:
            retake_score = round(float(np.clip(score + np.random.normal(12, 5), 30, 100)), 1)
            final_status = "Cleared" if retake_score >= PASS_THRESHOLD else "Not Cleared"
        else:
            retake_score = None
            final_status = "Cleared"

        evaluator = dept_evaluator.get(dept)
        if evaluator == pid:  # can't evaluate yourself
            evaluator = dept_commander.get(dept)

        rows.append({
            "person_id": pid,
            "department": dept,
            "exam_year": year,
            "standardization_score": score,
            "flight_clearance": "Cleared" if cleared_first_try else "Not Cleared",
            "retake_required": retake_required,
            "retake_score": retake_score,
            "final_clearance_status": final_status,
            "evaluator_id": evaluator,
        })

    exams_df = pd.DataFrame(rows)
    exams_df.to_csv("/home/claude/standardization_exams.csv", index=False)

    print(f"Total exam records: {len(exams_df)}")
    print(f"Retake required rate: {exams_df.retake_required.mean():.1%}")
    print(f"Final 'Not Cleared' rate: {(exams_df.final_clearance_status == 'Not Cleared').mean():.1%}")
    print()
    print("Avg score by rank level (sanity check — should rise slightly with seniority):")
    merged = exams_df.merge(personal_df[["person_id", "rank"]], on="person_id")
    print(merged.groupby("rank")["standardization_score"].mean().round(1).sort_values())


if __name__ == "__main__":
    main()
