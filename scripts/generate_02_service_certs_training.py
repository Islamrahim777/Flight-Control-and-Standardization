"""
Generates:
  - previous_service.csv   (Table 2: Əvvəlki xidmət)   — 1 row/person
  - certifications.csv     (Table 3: Sertifikatlar/dillər) — 1 row/person
  - tactical_training.csv  (Table 4: Taktiki təlimlər)  — 0..4 rows/person

Depends on personal.csv (must be generated first).
Run: python3 generate_02_service_certs_training.py
"""

import random
import numpy as np
import pandas as pd

from uav_dataset_config import REFERENCE_DATE

random.seed(43)
np.random.seed(43)

PREVIOUS_BRANCHES = [
    "Ground Forces", "Air Force", "Navy", "Special Forces", "Artillery",
    "Reconnaissance", "Communications & Engineering Troops", "Border Service",
]
PREVIOUS_BRANCH_WEIGHTS = [0.30, 0.12, 0.05, 0.10, 0.15, 0.10, 0.10, 0.08]

OTHER_LANGUAGES = ["Turkish", "French", "German"]

TRAINING_NAMES = [
    "Qartal Tactical Exercise", "Şahin Readiness Drill", "Border Watch Exercise",
    "Joint Operations Training", "NATO Partnership Training",
    "Regional Tactical Exercise", "Winter Readiness Drill", "Live Fire Exercise",
]
TRAINING_LEVELS = ["Battalion", "Brigade", "National", "International"]
TRAINING_LEVEL_WEIGHTS = [0.45, 0.30, 0.15, 0.10]
TRAINING_ROLES = ["Participant", "Instructor", "Observer"]
TRAINING_RESULTS = ["Passed", "Completed", "Failed"]


def generate_previous_service(personal_df):
    rows = []
    for _, r in personal_df.iterrows():
        if r.get("officer_commissioning_source") == "Prior Enlisted (Gizir) Commission":
            # Their pre-commission years were spent AS a UAV Operator in
            # this very unit — not an external branch.
            branch = "Internal Promotion (Former UAV Operator, this unit)"
            prior_years = r["years_as_enlisted_before_commission"]
        else:
            prior_years = round(r["total_military_service_years"] - r["uav_service_years"], 2)
            if prior_years < 0.5:
                branch, prior_years = "Civilian Sector (Direct Entry)", 0.0
            else:
                branch = random.choices(PREVIOUS_BRANCHES, weights=PREVIOUS_BRANCH_WEIGHTS)[0]
        rows.append({
            "person_id": r["person_id"],
            "previous_branch": branch,
            "years_in_previous_branch": prior_years,
        })
    return pd.DataFrame(rows)


def generate_certifications(personal_df, delayed_ids):
    rows = []
    for _, r in personal_df.iterrows():
        pid = r["person_id"]
        is_officer = r["rank_group"] == "Officer"
        is_lead = bool(r["is_leadership"])
        is_civilian_commission = r.get("officer_commissioning_source") == "Civilian Direct Commission"

        if pid in delayed_ids:
            # Rank-delayed people: no language skills, no NATO/foreign
            # training, no instructor certification.
            rows.append({
                "person_id": pid, "english_certified": False, "russian_certified": False,
                "other_language_certified": False, "other_language_name": None,
                "nato_training": False, "foreign_course": False, "instructor_certified": False,
            })
            continue

        # English certification is capped hard: it must NEVER exceed 10%
        # in any subgroup (kept low across the whole unit, by design).
        if is_civilian_commission:
            p_english = 0.10
        elif is_officer:
            p_english = 0.05
        else:
            p_english = 0.02

        p_russian = 0.55 + (0.05 if is_officer else 0)
        p_other = 0.10 + (0.06 if is_lead else 0)
        p_nato = 0.12 + (0.12 if is_officer else 0) + (0.13 if is_lead else 0)
        p_instructor = 0.10 + (0.10 if is_officer else 0) + (0.15 if is_lead else 0)
        p_foreign_base = 0.08

        if is_civilian_commission:  # civilian-university officers: stronger non-English foreign/other profile
            p_other += 0.15
            p_foreign_base += 0.25
        if not is_officer:  # gizirs across the board: much lower
            p_other *= 0.20
            p_nato *= 0.30
            p_foreign_base *= 0.30

        english = random.random() < min(p_english, 0.95)
        russian = random.random() < min(p_russian, 0.9)
        other = random.random() < min(p_other, 0.6)
        nato = random.random() < min(p_nato, 0.8)
        p_foreign = p_foreign_base + (0.30 if nato else 0)
        foreign_course = random.random() < min(p_foreign, 0.9)
        instructor_cert = random.random() < min(p_instructor, 0.6)

        rows.append({
            "person_id": pid,
            "english_certified": english,
            "russian_certified": russian,
            "other_language_certified": other,
            "other_language_name": random.choice(OTHER_LANGUAGES) if other else None,
            "nato_training": nato,
            "foreign_course": foreign_course,
            "instructor_certified": instructor_cert,
        })
    return pd.DataFrame(rows)


def generate_tactical_training(personal_df, delayed_ids):
    rows = []
    for _, r in personal_df.iterrows():
        if r["person_id"] in delayed_ids:
            continue  # rank-delayed people: no tactical training participation at all

        is_officer = r["rank_group"] == "Officer"
        # number of trainings attended 2021-2026 — much lower baseline for gizirs
        lam = (1.6 if is_officer else 0.35) + (0.8 if r["is_leadership"] else 0)
        n_trainings = np.random.poisson(lam)
        n_trainings = min(n_trainings, 5)
        used_years = set()
        for _ in range(n_trainings):
            year = random.randint(2021, 2026)
            role = random.choices(TRAINING_ROLES, weights=[0.75, 0.10, 0.15])[0]
            if role == "Instructor" and not is_officer:
                role = "Participant"  # only officers instruct, for realism
            score = round(np.clip(np.random.normal(78, 10), 40, 100), 1)
            result = "Failed" if score < 60 else random.choices(
                ["Passed", "Completed"], weights=[0.7, 0.3])[0]
            rows.append({
                "person_id": r["person_id"],
                "training_name": random.choice(TRAINING_NAMES),
                "level": random.choices(TRAINING_LEVELS, weights=TRAINING_LEVEL_WEIGHTS)[0],
                "year": year,
                "role": role,
                "result": result,
                "score": score,
            })
    return pd.DataFrame(rows)


def cap_english_rate(certs_df, personal_df, cap=0.10):
    """Hard guarantee: no subgroup's REALIZED english_certified rate may
    exceed `cap`, regardless of sampling noise. Randomly flips excess
    True -> False within each group until the cap holds exactly."""
    merged = certs_df.merge(
        personal_df[["person_id", "officer_commissioning_source", "rank_group"]], on="person_id")
    group_key = merged["officer_commissioning_source"].fillna(merged["rank_group"])
    for name, grp in merged.groupby(group_key):
        max_allowed = int(len(grp) * cap)
        true_ids = grp.loc[grp.english_certified == True, "person_id"].tolist()
        if len(true_ids) > max_allowed:
            to_flip = random.sample(true_ids, len(true_ids) - max_allowed)
            certs_df.loc[certs_df.person_id.isin(to_flip), "english_certified"] = False
    return certs_df


def main():
    personal_df = pd.read_csv("/home/claude/personal.csv")
    try:
        delay_df = pd.read_csv("/home/claude/rank_delay_analysis.csv")
        delayed_ids = set(delay_df[delay_df.rank_delayed == True]["person_id"])
    except FileNotFoundError:
        delayed_ids = set()

    prev_service_df = generate_previous_service(personal_df)
    certs_df = generate_certifications(personal_df, delayed_ids)
    certs_df = cap_english_rate(certs_df, personal_df, cap=0.10)
    tactical_df = generate_tactical_training(personal_df, delayed_ids)

    prev_service_df.to_csv("/home/claude/previous_service.csv", index=False)
    certs_df.to_csv("/home/claude/certifications.csv", index=False)
    tactical_df.to_csv("/home/claude/tactical_training.csv", index=False)

    print("=== Previous Service ===")
    print(prev_service_df["previous_branch"].value_counts())
    print()
    print("=== Certifications (rate of True) ===")
    print(certs_df[["english_certified", "russian_certified", "other_language_certified",
                     "nato_training", "foreign_course", "instructor_certified"]].mean())
    print()
    print("=== Tactical Training ===")
    print(f"Total training-participation rows: {len(tactical_df)}")
    print(f"People with 0 trainings: {525 - tactical_df['person_id'].nunique()}")
    print(tactical_df["result"].value_counts())


if __name__ == "__main__":
    main()
