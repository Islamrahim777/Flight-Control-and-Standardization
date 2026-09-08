"""
Generates:
  - flight_safety.csv   (Table 9: Uçuş təhlükəsizliyi)
    Sparse incident log. Incident probability scales with actual MISSION
    exposure (from mission_log.csv, one row per real flight — not the
    summed crew-hours in flight_operations.csv, which would overcount
    since 3 roles now log hours per mission) and the department's
    technical condition that year (from fuel_consumption.csv). Each
    incident is attributed to that mission's pilot.

Depends on mission_log.csv and fuel_consumption.csv.
Run: python3 generate_07_flight_safety.py
"""

import random
import numpy as np
import pandas as pd

random.seed(48)
np.random.seed(48)

BASE_RATE_PER_HOUR = 0.0009  # recalibrated for actual aircraft-hours (was tuned to the old, inflated crew-hour basis)

INCIDENT_TYPES = ["Technical Fault (no loss)", "Minor Incident", "Major Accident", "UAV Loss"]
INCIDENT_TYPE_WEIGHTS = [0.55, 0.25, 0.12, 0.08]

CAUSE_BY_TYPE = {
    "Technical Fault (no loss)": (["Mechanical Failure", "Unknown"], [0.8, 0.2]),
    "Minor Incident": (["Human Error", "Weather", "Mechanical Failure"], [0.45, 0.35, 0.20]),
    "Major Accident": (["Weather", "Mechanical Failure", "Human Error", "Enemy Action"], [0.35, 0.30, 0.25, 0.10]),
    "UAV Loss": (["Enemy Action", "Mechanical Failure", "Weather", "Human Error"], [0.30, 0.30, 0.25, 0.15]),
}

SEVERITY_RANGE_BY_TYPE = {
    "Technical Fault (no loss)": (1, 3),
    "Minor Incident": (2, 5),
    "Major Accident": (6, 9),
    "UAV Loss": (8, 10),
}


def outcome_for(cause, days_since):
    if days_since < 60 and random.random() < 0.5:
        return "Under Investigation"
    mapping = {
        "Mechanical Failure": "Corrective Action Taken",
        "Human Error": "Pilot Error",
        "Weather": "No Fault Found",
        "Enemy Action": "No Fault Found",
        "Unknown": "Under Investigation",
    }
    return mapping.get(cause, "Under Investigation")


def main():
    mission_log = pd.read_csv("/home/claude/mission_log.csv")
    fuel_df = pd.read_csv("/home/claude/fuel_consumption.csv")

    tech_lookup = fuel_df.set_index(["department", "year"])["avg_technical_condition_score"].to_dict()
    reference_ordinal = pd.Timestamp("2026-06-30").toordinal()

    # One row per actual mission, with its pilot, for incident attribution
    missions = mission_log[(mission_log.status == "Completed") & (mission_log.role_on_mission == "Pilot")]

    rows = []
    incident_counter = 1
    for _, r in missions.iterrows():
        tech_score = tech_lookup.get((r["department"], int(r["year"])), 90)
        rate = BASE_RATE_PER_HOUR * (1 + max(0, 90 - tech_score) * 0.012)
        expected = r["planned_duration_hours"] * rate
        n_incidents = np.random.poisson(expected)

        for _ in range(n_incidents):
            incident_type = random.choices(INCIDENT_TYPES, weights=INCIDENT_TYPE_WEIGHTS)[0]
            causes, cause_wts = CAUSE_BY_TYPE[incident_type]
            cause = random.choices(causes, weights=cause_wts)[0]

            incident_date = pd.Timestamp(r["mission_date"])
            days_since = reference_ordinal - incident_date.toordinal()

            lo, hi = SEVERITY_RANGE_BY_TYPE[incident_type]
            severity = random.randint(lo, hi)

            rows.append({
                "incident_id": f"INC{incident_counter:04d}",
                "mission_id": r["mission_id"],
                "person_id": r["person_id"],
                "department": r["department"],
                "incident_date": incident_date.date(),
                "incident_type": incident_type,
                "cause": cause,
                "severity_score": severity,
                "investigation_outcome": outcome_for(cause, days_since),
            })
            incident_counter += 1

    safety_df = pd.DataFrame(rows)
    safety_df.to_csv("/home/claude/flight_safety.csv", index=False)

    print(f"Total incidents: {len(safety_df)}")
    print(safety_df["incident_type"].value_counts())
    print()
    print("Incidents by department:")
    print(safety_df["department"].value_counts())
    print()
    print("Investigation outcome distribution:")
    print(safety_df["investigation_outcome"].value_counts())


if __name__ == "__main__":
    main()
