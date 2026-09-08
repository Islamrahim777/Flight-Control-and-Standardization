"""
Generates:
  - mission_log.csv         (NEW: one row per person PER MISSION — the crew log)
  - flight_operations.csv   (Table 5, derived: person-month aggregates from mission_log)

CREW MODEL (per user's correction): a single mission is flown by a crew,
not one independent person:
  - 1 Pilot-Operator flies/logs the FULL mission duration (no rotation)
  - UAV Operators rotate in ~4-hour shifts from the ground control station
  - Mission Commanders (Operations Officers) also rotate in ~4-hour shifts
  e.g. a 12-hour mission needs 1 pilot + 3 operators + 3 commanders
  (12h / 4h-shift = 3 shifts each for the rotating roles).

Missions are generated at the DEPARTMENT level (not per-person); crew for
each mission is drawn (weighted by each person's accumulated performance
modifier) from that department's pool of eligible specializations, so
stronger performers naturally get picked more often and accumulate more
hours over time.

Depends on personal.csv, certifications.csv, rank_delay_analysis.csv.
Run: python3 generate_03_flight_operations.py
"""

import random
import numpy as np
import pandas as pd
from datetime import date
from math import ceil

from uav_dataset_config import REFERENCE_DATE, DEPARTMENTS

random.seed(44)
np.random.seed(44)

DATASET_START = date(2021, 1, 1)
SHIFT_HOURS = 4.0

PILOT_POOL_SPECS = {"Pilot-Operator", "Pilot-Operator Lead"}
OPERATOR_POOL_SPECS = {"UAV Operator"}
COMMANDER_POOL_SPECS = {"Operations Officer", "Chief of Operations", "Department Commander"}

MONTH_MULTIPLIER = {1: 0.65, 2: 0.68, 3: 0.85, 4: 1.10, 5: 1.55, 6: 1.45,
                     7: 1.35, 8: 1.35, 9: 1.15, 10: 0.90, 11: 0.75, 12: 0.65}
WEATHER_BY_SEASON = {
    "winter": (["Clear", "Cloudy", "Rainy", "Stormy", "Windy"], [0.25, 0.30, 0.20, 0.10, 0.15]),
    "spring": (["Clear", "Cloudy", "Rainy", "Stormy", "Windy"], [0.45, 0.25, 0.15, 0.05, 0.10]),
    "summer": (["Clear", "Cloudy", "Rainy", "Stormy", "Windy"], [0.65, 0.20, 0.05, 0.02, 0.08]),
    "autumn": (["Clear", "Cloudy", "Rainy", "Stormy", "Windy"], [0.35, 0.30, 0.20, 0.05, 0.10]),
}
DEPT_BASE_LAMBDA = 16.0  # missions/month per department at neutral season

FEATURED_TOP_PERFORMERS = {"AO17018", "AO16543"}


def season_of(month):
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "autumn"


def person_join_month(uav_service_years: float):
    start = REFERENCE_DATE - pd.Timedelta(days=uav_service_years * 365.25)
    y, m = start.year, start.month
    if date(y, m, 1) < DATASET_START:
        return DATASET_START.year, DATASET_START.month
    return y, m


OFFICER_LEVEL = {"Lieutenant": 0, "Senior Lieutenant": 1, "Captain": 2, "Major": 3, "Lieutenant Colonel": 4}
WARRANT_LEVEL = {"Junior Warrant Officer": 0, "Warrant Officer": 1, "Senior Warrant Officer": 2}


def compute_weight(row, lang_bonus_ids, delayed_ids):
    """Selection weight for crew sampling — reuses every accumulated
    performance rule so stronger performers are picked more often.
    Also folds in the rank effect: more senior ranks fly LESS (more
    administrative burden), same finding as the original per-person model."""
    pid = row["person_id"]
    spec = row["specialization"]
    commissioning = row.get("officer_commissioning_source")
    academy_type = row.get("military_academy_type")

    lvl = OFFICER_LEVEL[row["rank"]] if row["rank_group"] == "Officer" else WARRANT_LEVEL[row["rank"]]
    w = max(0.45, 1 - 0.14 * lvl)

    if pid in FEATURED_TOP_PERFORMERS:
        w *= 1.30
    if spec == "Pilot-Operator" and commissioning in (
            "Prior Enlisted (Gizir) Commission", "Civilian Direct Commission"):
        w *= 1.20
    if academy_type == "Military Aviation School":
        w *= 1.25
    if pid in lang_bonus_ids:
        w *= 1.05
    if pid in delayed_ids:
        w *= 0.65
    return w


def weighted_sample(pool_df, n, weight_col="weight", allow_repeat=True):
    """Sample n people from pool_df, weighted, with or without repeats."""
    if pool_df.empty:
        return []
    weights = pool_df[weight_col].to_numpy()
    weights = weights / weights.sum()
    if not allow_repeat and n <= len(pool_df):
        idx = np.random.choice(len(pool_df), size=n, replace=False, p=weights)
    else:
        idx = np.random.choice(len(pool_df), size=n, replace=True, p=weights)
    return pool_df.iloc[idx]["person_id"].tolist()


def main():
    personal = pd.read_csv("/home/claude/personal.csv")
    certs = pd.read_csv("/home/claude/certifications.csv")
    delay = pd.read_csv("/home/claude/rank_delay_analysis.csv")

    lang_bonus_ids = set(certs[(certs.english_certified == True)
                                | (certs.other_language_certified == True)].person_id)
    delayed_ids = set(delay[delay.rank_delayed == True].person_id)

    personal["weight"] = personal.apply(lambda r: compute_weight(r, lang_bonus_ids, delayed_ids), axis=1)
    personal["join_year"], personal["join_month"] = zip(*personal["uav_service_years"].map(person_join_month))

    mission_rows = []
    mission_counter = 1
    end_y, end_m = REFERENCE_DATE.year, REFERENCE_DATE.month

    for dept in DEPARTMENTS:
        dept_people = personal[personal.department == dept]
        pilot_pool_all = dept_people[dept_people.specialization.isin(PILOT_POOL_SPECS)]
        operator_pool_all = dept_people[dept_people.specialization.isin(OPERATOR_POOL_SPECS)]
        commander_pool_all = dept_people[dept_people.specialization.isin(COMMANDER_POOL_SPECS)]

        y, m = DATASET_START.year, DATASET_START.month
        while (y, m) <= (end_y, end_m):
            season = season_of(m)
            lam = DEPT_BASE_LAMBDA * MONTH_MULTIPLIER[m]
            n_missions = np.random.poisson(lam)

            active = dept_people[(dept_people.join_year < y) |
                                  ((dept_people.join_year == y) & (dept_people.join_month <= m))]
            pilot_pool = pilot_pool_all[pilot_pool_all.person_id.isin(active.person_id)]
            operator_pool = operator_pool_all[operator_pool_all.person_id.isin(active.person_id)]
            commander_pool = commander_pool_all[commander_pool_all.person_id.isin(active.person_id)]

            for _ in range(n_missions):
                if pilot_pool.empty or operator_pool.empty or commander_pool.empty:
                    continue
                duration = float(np.clip(np.random.normal(17, 2), 10, 20))
                p_cancel = float(np.clip(0.08 + (1 - MONTH_MULTIPLIER[m]) * 0.25, 0.02, 0.40))
                cancelled = np.random.random() < p_cancel

                mission_id = f"MSN{mission_counter:05d}"
                mission_counter += 1
                day = random.randint(1, 28)
                mission_date = date(y, m, day)

                weather_opts, weather_wts = WEATHER_BY_SEASON[season]
                dominant_weather = random.choices(weather_opts, weights=weather_wts)[0]
                avg_temp = {"winter": random.uniform(-2, 8), "spring": random.uniform(10, 22),
                            "summer": random.uniform(24, 36), "autumn": random.uniform(8, 20)}[season]

                if cancelled:
                    mission_rows.append({
                        "mission_id": mission_id, "department": dept, "year": y, "month": m,
                        "mission_date": mission_date, "planned_duration_hours": round(duration, 2),
                        "status": "Cancelled",
                        "cancellation_reason": random.choices(
                            ["Weather", "Technical Fault", "Mission Change"], weights=[0.55, 0.30, 0.15])[0],
                        "dominant_weather": dominant_weather, "avg_temperature_c": round(avg_temp, 1),
                        "person_id": None, "role_on_mission": None, "shift_hours": 0.0,
                        "hours_category": None,
                    })
                    continue

                n_shifts = max(1, ceil(duration / SHIFT_HOURS))
                pilot_id = weighted_sample(pilot_pool, 1)[0]
                operator_ids = weighted_sample(operator_pool, n_shifts, allow_repeat=False)
                commander_ids = weighted_sample(commander_pool, n_shifts, allow_repeat=False)

                mix = np.random.dirichlet([2.0, 1.5, 1.0])  # training, combat, test
                category = random.choices(["Training", "Combat", "Test"], weights=mix)[0]

                crew = [(pilot_id, "Pilot", round(duration, 2))]
                remaining = duration
                for oid in operator_ids:
                    shift = min(SHIFT_HOURS, remaining)
                    crew.append((oid, "Operator", round(shift, 2)))
                    remaining -= shift
                remaining = duration
                for cid in commander_ids:
                    shift = min(SHIFT_HOURS, remaining)
                    crew.append((cid, "Mission Commander", round(shift, 2)))
                    remaining -= shift

                for pid, role, hrs in crew:
                    mission_rows.append({
                        "mission_id": mission_id, "department": dept, "year": y, "month": m,
                        "mission_date": mission_date, "planned_duration_hours": round(duration, 2),
                        "status": "Completed", "cancellation_reason": None,
                        "dominant_weather": dominant_weather, "avg_temperature_c": round(avg_temp, 1),
                        "person_id": pid, "role_on_mission": role, "shift_hours": hrs,
                        "hours_category": category,
                    })

            m += 1
            if m > 12:
                m, y = 1, y + 1

    mission_log = pd.DataFrame(mission_rows)
    mission_log.to_csv("/home/claude/mission_log.csv", index=False)

    # ---------------- Derive person-month flight_operations.csv ------------
    crew_rows = mission_log[mission_log.status == "Completed"]
    agg = crew_rows.groupby(["person_id", "department", "year", "month"]).agg(
        completed_missions=("mission_id", "nunique"),
        flight_hours_real=("shift_hours", "sum"),
    ).reset_index()

    cat_hours = (crew_rows.pivot_table(index=["person_id", "year", "month"], columns="hours_category",
                                        values="shift_hours", aggfunc="sum", fill_value=0)
                 .reset_index())
    for col in ["Training", "Combat", "Test"]:
        if col not in cat_hours.columns:
            cat_hours[col] = 0.0
    agg = agg.merge(cat_hours, on=["person_id", "year", "month"], how="left")
    agg = agg.rename(columns={"Training": "flight_hours_training", "Combat": "flight_hours_combat",
                               "Test": "flight_hours_test"})

    weather_month = (mission_log.groupby(["department", "year", "month"])
                     .agg(dominant_weather=("dominant_weather", lambda s: s.mode().iloc[0]),
                          avg_temperature_c=("avg_temperature_c", "mean")).reset_index())

    agg = agg.merge(weather_month, on=["department", "year", "month"], how="left")
    agg["avg_temperature_c"] = agg["avg_temperature_c"].round(1)

    rank_lookup = personal.set_index("person_id")[["rank_group", "rank"]]
    officer_level = {"Lieutenant": 0, "Senior Lieutenant": 1, "Captain": 2, "Major": 3, "Lieutenant Colonel": 4}
    warrant_level = {"Junior Warrant Officer": 0, "Warrant Officer": 1, "Senior Warrant Officer": 2}

    def sim_hours_for(pid):
        r = rank_lookup.loc[pid]
        lvl = officer_level[r["rank"]] if r["rank_group"] == "Officer" else warrant_level[r["rank"]]
        base = 6 - lvl * 0.6
        return round(float(np.clip(np.random.normal(max(base, 1.5), 2), 0, 15)), 2)

    agg["flight_hours_simulator"] = agg["person_id"].map(sim_hours_for)
    agg["planned_missions"] = agg["completed_missions"]
    agg["cancelled_missions"] = 0
    agg["avg_wind_speed_kmh"] = np.round(np.random.uniform(5, 45, size=len(agg)), 1)
    agg["primary_cancellation_reason"] = None

    flight_ops = agg[["person_id", "department", "year", "month", "planned_missions",
                       "completed_missions", "cancelled_missions", "flight_hours_real",
                       "flight_hours_training", "flight_hours_combat", "flight_hours_test",
                       "flight_hours_simulator", "avg_temperature_c", "avg_wind_speed_kmh",
                       "dominant_weather", "primary_cancellation_reason"]]
    flight_ops.to_csv("/home/claude/flight_operations.csv", index=False)

    print(f"Total missions: {mission_log.mission_id.nunique()}")
    print(f"Mission log rows (crew assignments): {len(mission_log)}")
    print(f"Flight-eligible people appearing: {flight_ops.person_id.nunique()}")
    print()
    print("Example: crew breakdown for one mission —")
    sample_mission = crew_rows.mission_id.iloc[0]
    print(crew_rows[crew_rows.mission_id == sample_mission]
          [["mission_id", "person_id", "role_on_mission", "shift_hours"]].to_string(index=False))
    print()
    print("Total flight hours by department:")
    print(flight_ops.groupby("department")["flight_hours_real"].sum().round(0))


if __name__ == "__main__":
    main()
