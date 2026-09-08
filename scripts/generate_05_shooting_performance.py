"""
Generates:
  - shooting_performance.csv   (Table 6: Atış performansı) — ONE ROW PER SHOT
    (not aggregated) so you can analyze first-shot failure rates, learning
    curves over time, and success rate by shot type / person / department.

Only people who actually operate or authorize weapon release get shot
records: Pilot-Operator, UAV Operator, Operations Officer,
Pilot-Operator Lead, Department Commander. ~12% of eligible people have
zero shots (never assigned a live/training engagement).

Depends on personal.csv.
Run: python3 generate_05_shooting_performance.py
"""

import random
import numpy as np
import pandas as pd
from datetime import date

from uav_dataset_config import REFERENCE_DATE

random.seed(46)
np.random.seed(46)

SHOOTING_SPECS = {
    "Pilot-Operator": 0.03, "UAV Operator": 0.00, "Operations Officer": -0.05,
    "Pilot-Operator Lead": 0.02, "Department Commander": -0.05,
}

SHOT_TYPES = ["PUA", "Laser-guided", "Artillery Spotting", "Training"]
SHOT_TYPE_WEIGHTS = [0.45, 0.25, 0.15, 0.15]
SHOT_TYPE_BASE_SUCCESS = {"PUA": 0.82, "Laser-guided": 0.85,
                           "Artillery Spotting": 0.78, "Training": 0.90}

DATASET_START = date(2021, 1, 1)


FEATURED_TOP_PERFORMERS = {"AO17018", "AO16543"}  # Capt. Yaqubov, Capt. Qurbanov


def compute_shooting_bonus(row, lang_bonus_ids, delayed_ids):
    """Same accumulated performance rules as flight operations, expressed
    as an additive bonus/penalty to shooting success probability."""
    pid = row["person_id"]
    spec = row["specialization"]
    commissioning = row.get("officer_commissioning_source")
    academy_type = row.get("military_academy_type")

    bonus = 0.0
    if pid in FEATURED_TOP_PERFORMERS:
        bonus += 0.10
    if spec == "Pilot-Operator" and commissioning in (
            "Prior Enlisted (Gizir) Commission", "Civilian Direct Commission"):
        bonus += 0.08
    if academy_type == "Military Aviation School":
        bonus += 0.07
    if pid in lang_bonus_ids:
        bonus += 0.03
    if pid in delayed_ids:
        bonus -= 0.10
    return bonus


def person_start_date(uav_service_years: float) -> date:
    start = REFERENCE_DATE - pd.Timedelta(days=uav_service_years * 365.25)
    return max(start.date() if hasattr(start, "date") else start, DATASET_START)


def random_date_between(start: date, end: date) -> date:
    span = (end - start).days
    if span <= 0:
        return start
    return start + pd.Timedelta(days=random.randint(0, span))


def generate_for_person(row, lang_bonus_ids, delayed_ids):
    spec = row["specialization"]
    if spec not in SHOOTING_SPECS:
        return []
    if random.random() < 0.12:  # never fired
        return []

    start = person_start_date(row["uav_service_years"])
    end = REFERENCE_DATE
    tenure_years = max(row["uav_service_years"], 0.1)

    n_shots = int(np.clip(np.random.poisson(3 + tenure_years * 3), 0, 40))
    if n_shots == 0:
        return []

    # Persistent per-person "marksmanship" offset — some people are just
    # consistently better/worse shots than average.
    skill_offset = float(np.clip(np.random.normal(0, 0.06), -0.15, 0.15))
    spec_bonus = SHOOTING_SPECS[spec]
    accumulated_bonus = compute_shooting_bonus(row, lang_bonus_ids, delayed_ids)

    dates = sorted(random_date_between(start, end) for _ in range(n_shots))

    out = []
    for seq, shot_date in enumerate(dates, start=1):
        shot_type = random.choices(SHOT_TYPES, weights=SHOT_TYPE_WEIGHTS)[0]
        p = SHOT_TYPE_BASE_SUCCESS[shot_type] + spec_bonus + skill_offset + accumulated_bonus
        p += min(0.15, seq * 0.006)          # gradual learning curve
        if seq == 1:
            p -= 0.25                          # first-shot penalty
        p = float(np.clip(p, 0.05, 0.98))

        outcome = "Successful" if random.random() < p else "Failed"
        out.append({
            "shot_id": f"{row['person_id']}-S{seq:03d}",
            "person_id": row["person_id"],
            "department": row["department"],
            "shot_date": shot_date,
            "shot_sequence_number": seq,
            "is_first_shot": seq == 1,
            "shot_type": shot_type,
            "outcome": outcome,
        })
    return out


def main():
    personal_df = pd.read_csv("/home/claude/personal.csv")
    certs_df = pd.read_csv("/home/claude/certifications.csv")
    delay_df = pd.read_csv("/home/claude/rank_delay_analysis.csv")

    lang_bonus_ids = set(certs_df[(certs_df.english_certified == True)
                                   | (certs_df.other_language_certified == True)].person_id)
    delayed_ids = set(delay_df[delay_df.rank_delayed == True].person_id)

    all_rows = []
    for _, row in personal_df.iterrows():
        all_rows.extend(generate_for_person(row, lang_bonus_ids, delayed_ids))

    shots_df = pd.DataFrame(all_rows)
    shots_df.to_csv("/home/claude/shooting_performance.csv", index=False)

    print(f"Total shots: {len(shots_df)}")
    print(f"Shooters with >=1 shot: {shots_df['person_id'].nunique()}")
    print()
    print("Overall success rate:", round((shots_df.outcome == "Successful").mean(), 3))
    print("First-shot success rate:",
          round((shots_df[shots_df.is_first_shot].outcome == "Successful").mean(), 3))
    print("Non-first-shot success rate:",
          round((shots_df[~shots_df.is_first_shot].outcome == "Successful").mean(), 3))
    print()
    print("Success rate by shot type:")
    print(shots_df.groupby("shot_type").outcome.apply(lambda s: (s == "Successful").mean()).round(3))
    print()
    print("Per-person total shots & success rate (distribution check):")
    per_person = shots_df.groupby("person_id").agg(
        total_shots=("outcome", "count"),
        success_rate=("outcome", lambda s: round((s == "Successful").mean(), 3)))
    print(per_person["total_shots"].describe())
    print(per_person["success_rate"].describe())


if __name__ == "__main__":
    main()
