"""
Generates:
  - fuel_consumption.csv   (Table 8: Yanacaq sərfiyyatı) — department x year grain

Uses AIRCRAFT hours (each mission counted ONCE, from mission_log.csv),
not the summed crew-hours in flight_operations.csv — since a mission now
has multiple crew members logging hours (pilot + rotating operators +
commanders), summing THEIR hours would massively overcount actual fuel
burn (the airframe only flies once per mission).

All departments fly the same UAV model (Bayraktar TB2, ~15 L/hour baseline)
per the user's own number; fuel burn varies slightly by department/year
via a persistent "technical condition" bias (some departments keep their
airframes better maintained than others) plus year-to-year noise — this
is what a "which department is more fuel-efficient" dashboard compares.

Depends on mission_log.csv.
Run: python3 generate_04_fuel_consumption.py
"""

import random
import numpy as np
import pandas as pd

from uav_dataset_config import DEPARTMENTS

random.seed(45)
np.random.seed(45)

YEARS = [2021, 2022, 2023, 2024, 2025, 2026]

# Persistent per-department technical-quality bias (points on a 0-100 scale).
DEPT_TECH_BIAS = {"Alpha": +3, "Beta": 0, "Delta": -2, "Gamma": +2, "Sigma": -4}

BASE_BURN_RATE = 15.0  # liters/hour, as specified


def main():
    mission_log = pd.read_csv("/home/claude/mission_log.csv")

    # One row per actual mission (aircraft hours), not per crew assignment
    missions = (mission_log[mission_log.status == "Completed"]
                .drop_duplicates("mission_id")
                [["mission_id", "department", "year", "planned_duration_hours"]])
    completed_ct = mission_log[mission_log.status == "Completed"].drop_duplicates("mission_id")

    agg = (missions.groupby(["department", "year"])
           .agg(total_aircraft_hours=("planned_duration_hours", "sum"),
                total_missions=("mission_id", "nunique"))
           .reset_index())

    # Simulator hours still come from flight_operations.csv (independent of crew model)
    flight_df = pd.read_csv("/home/claude/flight_operations.csv")
    sim_hours = (flight_df.groupby(["department", "year"])["flight_hours_simulator"]
                 .sum().reset_index())
    agg = agg.merge(sim_hours, on=["department", "year"], how="left")

    rows = []
    for _, r in agg.iterrows():
        dept, year = r["department"], int(r["year"])
        tech_score = float(np.clip(90 + DEPT_TECH_BIAS[dept] + np.random.normal(0, 3), 70, 99))
        burn_rate = round(BASE_BURN_RATE * (1 + (90 - tech_score) * 0.006), 2)
        total_fuel = round(r["total_aircraft_hours"] * burn_rate, 1)
        est_flying_days = min(300, int(r["total_missions"]))  # ~1 mission/day assumption

        rows.append({
            "department": dept,
            "year": year,
            "total_flight_hours_real": round(r["total_aircraft_hours"], 1),
            "total_flight_hours_simulator": round(r["flight_hours_simulator"], 1),
            "primary_uav_model": "Bayraktar TB2",
            "avg_technical_condition_score": round(tech_score, 1),
            "fuel_burn_rate_l_per_hour": burn_rate,
            "total_fuel_liters": total_fuel,
            "estimated_flying_days": int(est_flying_days),
        })

    fuel_df = pd.DataFrame(rows).sort_values(["department", "year"])
    fuel_df.to_csv("/home/claude/fuel_consumption.csv", index=False)

    print(fuel_df.to_string(index=False))
    print()
    print("Total fuel by department (2021-2026):")
    print(fuel_df.groupby("department")["total_fuel_liters"].sum().round(0))
    print()
    print("Avg fuel burn rate (L/h) by department:")
    print(fuel_df.groupby("department")["fuel_burn_rate_l_per_hour"].mean().round(2)
          .sort_values())


if __name__ == "__main__":
    main()
