"""
Generates:
  - medals.csv   (Table 10: Mükafatlar/medallar) — one row per medal awarded.

DESIGN INTENT (per user's explicit request): medal count should have
only a WEAK relationship with real performance. A merit score is built
from shooting success rate, total flight hours, NATO training and
foreign-course participation — but it only mildly nudges a Poisson
lambda that is dominated by random noise, a per-department "generosity"
bias, and a leadership bonus (commanders get recognized more regardless
of front-line performance). This is what produces cases like "98%
success + 1200 flight hours -> 1 medal" next to "82% success + 600
hours -> 4 medals", and is meant to surface as a "reward system may be
unfair" finding in your correlation analysis.

Depends on personal.csv, shooting_performance.csv, flight_operations.csv,
certifications.csv.
Run: python3 generate_09_medals.py
"""

import random
import numpy as np
import pandas as pd
from datetime import date

from uav_dataset_config import REFERENCE_DATE

random.seed(49)
np.random.seed(49)

DATASET_START = date(2021, 1, 1)
MAX_MEDALS_PER_PERSON = 6

# Some departments are just more generous with medals than others,
# independent of merit ("award-system unfairness" by department).
DEPT_MEDAL_BIAS = {"Alpha": 0.0, "Beta": 0.3, "Delta": -0.3, "Gamma": 0.5, "Sigma": -0.5}
LEADERSHIP_BONUS = 0.4  # leaders get recognized more regardless of front-line performance
FEATURED_TOP_PERFORMERS = {"AO17018", "AO16543"}

MEDAL_TYPES_AND_REASONS = [
    ("Meritorious Service Medal", "Sustained high standard of duty performance"),
    ("Distinguished Marksmanship Medal", "Recognized shooting proficiency"),
    ("Operational Excellence Medal", "Exceptional performance during operational missions"),
    ("International Cooperation Medal", "Contribution to joint/NATO training exercises"),
    ("Years of Service Medal", "Long and continuous military service"),
    ("Presidential Commendation", "Distinguished service recognized at command level"),
    ("Unit Commendation", "Contribution to unit-level achievement"),
]


def zscore(series):
    s = series.astype(float)
    std = s.std()
    if std == 0 or np.isnan(std):
        return s * 0
    return (s - s.mean()) / std


def person_start_date(uav_service_years: float) -> date:
    start = REFERENCE_DATE - pd.Timedelta(days=uav_service_years * 365.25)
    start = start.date() if hasattr(start, "date") else start
    return max(start, DATASET_START)


def main():
    personal_df = pd.read_csv("/home/claude/personal.csv")
    shots_df = pd.read_csv("/home/claude/shooting_performance.csv")
    flight_df = pd.read_csv("/home/claude/flight_operations.csv")
    certs_df = pd.read_csv("/home/claude/certifications.csv")
    delay_df = pd.read_csv("/home/claude/rank_delay_analysis.csv")
    delayed_ids = set(delay_df[delay_df.rank_delayed == True].person_id)

    # --- Build a merit table -------------------------------------------
    success_rate = (shots_df.groupby("person_id")["outcome"]
                     .apply(lambda s: (s == "Successful").mean()))
    total_hours = flight_df.groupby("person_id")["flight_hours_real"].sum()

    merit = personal_df[["person_id", "department", "is_leadership", "uav_service_years",
                          "military_academy_type"]].copy()
    merit = merit.merge(success_rate.rename("success_rate"), on="person_id", how="left")
    merit = merit.merge(total_hours.rename("total_flight_hours"), on="person_id", how="left")
    merit = merit.merge(certs_df[["person_id", "nato_training", "foreign_course"]],
                         on="person_id", how="left")
    merit["success_rate"] = merit["success_rate"].fillna(0)
    merit["total_flight_hours"] = merit["total_flight_hours"].fillna(0)
    merit["nato_training"] = merit["nato_training"].fillna(False)
    merit["foreign_course"] = merit["foreign_course"].fillna(False)

    merit_z = (0.35 * zscore(merit["success_rate"])
               + 0.35 * zscore(merit["total_flight_hours"])
               + 0.15 * merit["nato_training"].astype(float)
               + 0.15 * merit["foreign_course"].astype(float))

    rows = []
    medal_counter = 1
    lambdas, counts = [], []
    for idx, r in merit.iterrows():
        dept_bias = DEPT_MEDAL_BIAS[r["department"]]
        lead_bonus = LEADERSHIP_BONUS if r["is_leadership"] else 0.0
        delay_penalty = -0.5 if r["person_id"] in delayed_ids else 0.0
        featured_bonus = 0.5 if r["person_id"] in FEATURED_TOP_PERFORMERS else 0.0
        academy_bonus = 0.2 if r["military_academy_type"] == "Military Aviation School" else 0.0
        noise = np.random.normal(0, 1.5)  # large noise dominates the small merit term
        lam = max(0.05, 1.6 + 0.4 * merit_z[idx] + dept_bias + lead_bonus
                  + delay_penalty + featured_bonus + academy_bonus + noise)
        n_medals = min(np.random.poisson(lam), MAX_MEDALS_PER_PERSON)
        if r["person_id"] in FEATURED_TOP_PERFORMERS:
            n_medals = max(n_medals, 2)  # floor so "best personnel" status stays consistent
        lambdas.append(lam)
        counts.append(n_medals)

        start = person_start_date(r["uav_service_years"])
        span_days = max((REFERENCE_DATE - start).days, 1)
        for _ in range(n_medals):
            medal_type, reason = random.choice(MEDAL_TYPES_AND_REASONS)
            award_date = start + pd.Timedelta(days=random.randint(0, span_days))
            rows.append({
                "medal_id": f"M{medal_counter:04d}",
                "person_id": r["person_id"],
                "department": r["department"],
                "medal_type": medal_type,
                "award_date": award_date.date() if hasattr(award_date, "date") else award_date,
                "reason": reason,
            })
            medal_counter += 1

    medals_df = pd.DataFrame(rows)
    medals_df.to_csv("/home/claude/medals.csv", index=False)

    # --- Verify the correlation is weak, not zero, not strong -----------
    merit["medal_count"] = counts
    corr_success = merit["medal_count"].corr(merit["success_rate"])
    corr_hours = merit["medal_count"].corr(merit["total_flight_hours"])

    print(f"Total medals awarded: {len(medals_df)}")
    print(f"People with >=1 medal: {(merit.medal_count > 0).sum()} / {len(merit)}")
    print(f"Medal count distribution:\n{merit.medal_count.value_counts().sort_index()}")
    print()
    print(f"Correlation medal_count vs success_rate: {corr_success:.3f}")
    print(f"Correlation medal_count vs total_flight_hours: {corr_hours:.3f}")
    print()
    print("Example mismatches (high performance, low medals):")
    mism = merit[(merit.success_rate >= 0.9) & (merit.total_flight_hours >= 800)]
    print(mism[["person_id", "success_rate", "total_flight_hours", "medal_count"]]
          .sort_values("medal_count").head(5).to_string(index=False))
    print()
    print("Example mismatches (low performance, high medals):")
    mism2 = merit[(merit.success_rate <= 0.85) & (merit.total_flight_hours <= 700)]
    print(mism2[["person_id", "success_rate", "total_flight_hours", "medal_count"]]
          .sort_values("medal_count", ascending=False).head(5).to_string(index=False))
    print()
    print("Avg medal count by department (favoritism check):")
    print(merit.groupby("department")["medal_count"].mean().round(2))
    print()
    print("Avg medal count: leadership vs non-leadership:")
    print(merit.groupby("is_leadership")["medal_count"].mean().round(2))


if __name__ == "__main__":
    main()
