"""
Generates:
  - aircraft.csv                    (fleet master: 4 airframes per department)
  - aircraft_monthly_maintenance.csv (aircraft x month ground maintenance)
  - mission_technical_log.csv        (ONE ROW PER MISSION: aircraft used,
                                       pre-flight check, in-flight problems,
                                       early-return shortfall vs planned duration)

CAUSAL MODEL (weak-but-real, same philosophy as the rest of this dataset):
  - Each aircraft has a persistent base_condition (70-98), linked to its
    department's technical culture (reuses the same bias direction as
    fuel_consumption's tech score) plus individual airframe noise.
  - Each month, an aircraft gets a maintenance_hours figure. More
    maintenance hours nudge that aircraft's EFFECTIVE condition for the
    month upward (proactive maintenance helps) — capped, with heavy noise,
    so the relationship is real but not dominant.
  - Effective condition then (weakly) drives: pre-flight issue-found rate,
    in-flight technical-problem rate, and how many hours a problem
    mission returns early relative to its planned duration.

This lets you test: "does more ground maintenance time reduce in-flight
problems?" and "which department's aircraft are most reliable / cause
the least delay?"

Depends on personal.csv (technicians), mission_log.csv, fuel_consumption.csv.
Run: python3 generate_13_aircraft_technical.py
"""

import random
import numpy as np
import pandas as pd
from datetime import date

from uav_dataset_config import REFERENCE_DATE, DEPARTMENTS

random.seed(52)
np.random.seed(52)

AIRCRAFT_PER_DEPT = 4
DEPT_TECH_BIAS = {"Alpha": +3, "Beta": 0, "Delta": -2, "Gamma": +2, "Sigma": -4}  # same bias family as fuel_consumption

PROBLEM_TYPES = ["Engine", "Navigation/GPS", "Communication Link", "Sensor/Payload",
                  "Control Surface", "Electrical System"]
YEARS = list(range(2021, 2027))


def main():
    personal = pd.read_csv("/home/claude/personal.csv")
    mission_log = pd.read_csv("/home/claude/mission_log.csv")

    # ================= 1) Aircraft master table =========================
    aircraft_rows = []
    aircraft_by_dept = {}
    for dept in DEPARTMENTS:
        fleet = []
        for i in range(1, AIRCRAFT_PER_DEPT + 1):
            aircraft_id = f"TB2-{dept[:1].upper()}{i:02d}"
            in_service_year = random.randint(2020, 2023)
            base_condition = float(np.clip(88 + DEPT_TECH_BIAS[dept] + np.random.normal(0, 5), 65, 99))
            aircraft_rows.append({
                "aircraft_id": aircraft_id, "department": dept, "model": "Bayraktar TB2",
                "in_service_date": date(in_service_year, random.randint(1, 12), random.randint(1, 28)),
                "base_condition_score": round(base_condition, 1),
            })
            fleet.append(aircraft_id)
        aircraft_by_dept[dept] = fleet
    aircraft_df = pd.DataFrame(aircraft_rows)
    aircraft_df.to_csv("/home/claude/aircraft.csv", index=False)
    aircraft_lookup = aircraft_df.set_index("aircraft_id")["base_condition_score"].to_dict()
    aircraft_dept_lookup = aircraft_df.set_index("aircraft_id")["department"].to_dict()
    aircraft_in_service = aircraft_df.set_index("aircraft_id")["in_service_date"].to_dict()

    # ================= 2) Assign an aircraft to every completed mission ===
    missions = (mission_log[mission_log.status == "Completed"]
                .drop_duplicates("mission_id")
                [["mission_id", "department", "year", "month", "mission_date", "planned_duration_hours"]]
                .reset_index(drop=True))
    aircraft_in_service_ts = {aid: pd.Timestamp(d) for aid, d in aircraft_in_service.items()}

    def pick_aircraft(row):
        eligible = [a for a in aircraft_by_dept[row["department"]]
                    if (row["year"], row["month"]) >= (aircraft_in_service_ts[a].year, aircraft_in_service_ts[a].month)]
        if not eligible:
            eligible = aircraft_by_dept[row["department"]]  # fallback: fleet not yet established, use any
        return random.choice(eligible)

    missions["aircraft_id"] = missions.apply(pick_aircraft, axis=1)

    # ================= 3) Monthly maintenance per aircraft ================
    maint_rows = []
    effective_condition = {}  # (aircraft_id, year, month) -> effective condition this month
    for aircraft_id in aircraft_df.aircraft_id:
        base = aircraft_lookup[aircraft_id]
        in_service_ts = pd.Timestamp(aircraft_in_service[aircraft_id])
        for year in YEARS:
            for month in range(1, 13):
                if year == REFERENCE_DATE.year and month > REFERENCE_DATE.month:
                    continue
                if (year, month) < (in_service_ts.year, in_service_ts.month):
                    continue  # aircraft wasn't in service yet
                # AIRCRAFT AGE effect (per user correction): the OPPOSITE of
                # organizational learning — as each individual airframe ages,
                # it needs MORE maintenance and its condition gets WORSE
                # (wear and tear), not better.
                age_years = max(0, year - in_service_ts.year)
                maint_mean = 12 + age_years * 1.5   # older aircraft need more hours
                age_penalty = age_years * 1.6         # older aircraft: worse condition

                maint_hours = float(np.clip(np.random.normal(maint_mean, 5), 4, 45))
                # Maintenance still helps THIS month a bit, but the underlying age penalty dominates over time
                boost = min(8.0, max(0, maint_hours - 12) * 0.35)
                eff = float(np.clip(base + boost - age_penalty + np.random.normal(0, 3), 40, 100))
                effective_condition[(aircraft_id, year, month)] = eff

                technician_pool = personal[(personal.department == aircraft_dept_lookup[aircraft_id])
                                            & (personal.specialization.isin(
                                                ["Technical Staff", "Technical Service", "Repair Specialist"]))]
                technician_id = (technician_pool.sample(1).person_id.iloc[0]
                                  if not technician_pool.empty else None)

                maint_rows.append({
                    "aircraft_id": aircraft_id, "department": aircraft_dept_lookup[aircraft_id],
                    "year": year, "month": month, "maintenance_hours": round(maint_hours, 1),
                    "technician_id": technician_id,
                    "effective_condition_score": round(eff, 1),
                })
    maint_df = pd.DataFrame(maint_rows)
    maint_df.to_csv("/home/claude/aircraft_monthly_maintenance.csv", index=False)

    # ================= 4) Per-mission technical log ========================
    tech_rows = []
    for _, r in missions.iterrows():
        eff = effective_condition.get((r["aircraft_id"], r["year"], r["month"]),
                                       aircraft_lookup[r["aircraft_id"]])
        in_service_year = pd.Timestamp(aircraft_in_service[r["aircraft_id"]]).year
        age_years = max(0, r["year"] - in_service_year)

        # --- Pre-flight AND post-flight inspection (per user: starts ~1h when
        # new, rises toward ~2h as the airframe ages) ---
        check_base_minutes = 60 + min(age_years, 6) * 10  # 60min at age 0 -> ~120min at age 6
        pre_flight_minutes = float(np.clip(np.random.normal(check_base_minutes, 12), 30, 150))
        post_flight_minutes = float(np.clip(np.random.normal(check_base_minutes, 12), 30, 150))

        p_preflight_issue = float(np.clip(0.03 + (100 - eff) * 0.009, 0.02, 0.45))
        preflight_issue_found = np.random.random() < p_preflight_issue
        if preflight_issue_found:
            pre_flight_minutes += float(np.clip(np.random.normal(45, 20), 10, 120))

        # --- In-flight technical problem ---
        p_inflight_problem = float(np.clip(0.015 + (100 - eff) * 0.007, 0.01, 0.35))
        had_problem = np.random.random() < p_inflight_problem

        planned = r["planned_duration_hours"]
        if had_problem:
            problem_type = random.choice(PROBLEM_TYPES)
            severity_roll = np.random.random()
            if severity_roll < 0.55:
                # Resolved in-flight, no early return, but logged duration of the issue
                problem_duration_minutes = round(float(np.clip(np.random.normal(25, 10), 5, 90)), 1)
                actual_duration = planned
                hours_returned_early = 0.0
            else:
                # Caused an early return
                hours_returned_early = round(float(np.clip(np.random.exponential(2.5), 0.2, planned - 1)), 2)
                actual_duration = round(planned - hours_returned_early, 2)
                problem_duration_minutes = round(hours_returned_early * 60, 1)
        else:
            problem_type = None
            problem_duration_minutes = 0.0
            actual_duration = planned
            hours_returned_early = 0.0

        tech_rows.append({
            "mission_id": r["mission_id"], "aircraft_id": r["aircraft_id"],
            "department": r["department"], "year": r["year"], "month": r["month"],
            "mission_date": r["mission_date"], "aircraft_age_years": age_years,
            "planned_duration_hours": planned, "actual_duration_hours": actual_duration,
            "hours_returned_early": hours_returned_early,
            "pre_flight_check_minutes": round(pre_flight_minutes, 1),
            "pre_flight_issue_found": preflight_issue_found,
            "post_flight_check_minutes": round(post_flight_minutes, 1),
            "had_inflight_technical_problem": had_problem,
            "problem_type": problem_type,
            "problem_duration_minutes": problem_duration_minutes,
            "effective_condition_score": round(eff, 1),
        })

    tech_df = pd.DataFrame(tech_rows)
    tech_df.to_csv("/home/claude/mission_technical_log.csv", index=False)

    # ---------------- Sanity checks -----------------------------------------
    print(f"Aircraft: {len(aircraft_df)}  |  Maintenance rows: {len(maint_df)}  |  "
          f"Mission technical rows: {len(tech_df)}")
    print()
    print("In-flight problem rate by department:")
    print(tech_df.groupby("department").had_inflight_technical_problem.mean().round(3))
    print()
    print("Avg hours returned early by department (only when problem caused early return):")
    early = tech_df[tech_df.hours_returned_early > 0]
    print(early.groupby("department").hours_returned_early.mean().round(2))
    print()
    print("Correlation: monthly maintenance_hours vs that month's effective_condition_score:",
          round(maint_df.maintenance_hours.corr(maint_df.effective_condition_score), 3))
    merged = tech_df.merge(
        maint_df[["aircraft_id", "year", "month", "maintenance_hours"]],
        on=["aircraft_id", "year", "month"], how="left")
    print("Correlation: maintenance_hours vs in-flight problem occurring:",
          round(merged.maintenance_hours.corr(merged.had_inflight_technical_problem.astype(int)), 3))
    print()
    print("Aircraft reliability ranking (avg effective condition):")
    print(maint_df.groupby("aircraft_id").effective_condition_score.mean().round(1).sort_values(ascending=False).head(5))
    print()
    print("AIRCRAFT-AGE DEGRADATION TREND (per user correction — older = worse):")
    print("Avg pre/post-flight check minutes by aircraft age:")
    print(tech_df.groupby("aircraft_age_years")[["pre_flight_check_minutes", "post_flight_check_minutes"]].mean().round(1))
    print("In-flight problem rate by aircraft age:")
    print(tech_df.groupby("aircraft_age_years").had_inflight_technical_problem.mean().round(3))
    print("Effective condition score by aircraft age:")
    print(tech_df.groupby("aircraft_age_years").effective_condition_score.mean().round(1))


if __name__ == "__main__":
    main()
