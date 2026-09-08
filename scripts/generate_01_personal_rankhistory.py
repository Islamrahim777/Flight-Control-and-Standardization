"""
Generates:
  - personal.csv       (Table 1: Personal)
  - rank_history.csv   (Table 11: Rank History)

Run: python3 generate_01_personal_rankhistory.py
"""

import random
import numpy as np
import pandas as pd
from datetime import date

from uav_dataset_config import (
    REFERENCE_DATE, DEPARTMENTS, DEPT_COMPOSITION,
    OFFICER_RANKS, OFFICER_RANK_RANGES,
    WARRANT_RANKS, WARRANT_RANK_RANGES,
    REGULAR_OFFICER_RANK_WEIGHTS, LEADERSHIP_COMMANDER_RANK_WEIGHTS,
    LEADERSHIP_OTHER_RANK_WEIGHTS, REGULAR_WARRANT_RANK_WEIGHTS,
    LEADERSHIP_TECH_LEAD_RANK_WEIGHTS,
    OFFICER_SPECIALIZATIONS, WARRANT_SPECIALIZATIONS, LEADERSHIP_ROLES,
    AZ_REGIONS, make_full_name, sample_rank_and_service, years_before,
    make_fin_code, make_id_card_number, make_military_ticket_number,
    make_driving_license_number,
)

PUA_MAX_YEARS = 6.0          # dataset window is only ~2021-2026
ROTATION_CYCLE_YEARS = 3.0   # stated rule: rotation happens 3y after arrival


def build_person_row(person_id, department, rank_group, rank, total_service_years,
                      specialization, is_leadership, leadership_role, gender):
    # --- education / commissioning path / age ---------------------------
    is_officer = rank_group == "Officer"

    if is_officer:
        # THREE paths to becoming an officer:
        #   1) Military Academy        (traditional track)
        #   2) Civilian Direct Commission (university degree -> direct entry)
        #   3) Prior Enlisted (Gizir) Commission (was a UAV Operator, then
        #      commissioned as an officer later in their career)
        # Department Commander is reserved almost entirely for the
        # traditional Military Academy track (top command); other
        # leadership roles allow a modest share of both alternative paths;
        # regular officers have the most mixed pipeline.
        if leadership_role == "Department Commander":
            p_civilian, p_prior_enlisted = 0.08, 0.0
        elif is_leadership:
            p_civilian, p_prior_enlisted = 0.12, 0.13
        else:
            p_civilian, p_prior_enlisted = 0.28, 0.20

        roll = random.random()
        if roll < p_prior_enlisted:
            commissioning_source = "Prior Enlisted (Gizir) Commission"
            education_level = "In-Service Officer Commissioning Program"
            program_length = 2  # entered originally via the shorter enlisted track
            military_academy_type = None
        elif roll < p_prior_enlisted + p_civilian:
            commissioning_source = "Civilian Direct Commission"
            education_level = "Higher Civilian Education"
            program_length = 4
            military_academy_type = None
        else:
            commissioning_source = "Military Academy"
            education_level = "Higher Military Education"
            program_length = 4
            # Aviation-school graduates tend to be the stronger pilots/
            # mission commanders within the Military Academy pipeline.
            military_academy_type = random.choices(
                ["Military Aviation School", "General Military Academy"],
                weights=[0.40, 0.60])[0]

        if commissioning_source == "Prior Enlisted (Gizir) Commission":
            years_as_enlisted = round(min(random.uniform(1, 4), max(total_service_years - 1, 1)), 2)
            prior_enlisted_specialization = "UAV Operator"
        else:
            years_as_enlisted = None
            prior_enlisted_specialization = None
    else:
        program_length = 2
        education_level = "Vocational/Technical College"
        commissioning_source = None
        years_as_enlisted = None
        prior_enlisted_specialization = None
        military_academy_type = None

    entry_age = random.uniform(18, 20)                 # age at admission
    commission_age = entry_age + program_length
    age_at_reference = commission_age + total_service_years
    birth_date = years_before(REFERENCE_DATE, age_at_reference)
    age = int(age_at_reference)

    admission_year = REFERENCE_DATE.year - round(total_service_years) - program_length
    graduation_year = admission_year + program_length

    # --- PUA / department tenure ----------------------------------------
    uav_service_years = round(min(total_service_years, random.uniform(1, PUA_MAX_YEARS)), 2)
    if years_as_enlisted is not None:
        # Their gizir years were spent IN this unit (as UAV Operator), so
        # total PUA/unit tenure must cover that period plus some officer time.
        min_required = min(years_as_enlisted + random.uniform(0.2, 1.5), total_service_years, PUA_MAX_YEARS)
        uav_service_years = round(max(uav_service_years, min_required), 2)
    rotation_count = int(uav_service_years // ROTATION_CYCLE_YEARS)
    current_dept_years = round(uav_service_years - rotation_count * ROTATION_CYCLE_YEARS, 2)
    last_rotation_date = years_before(REFERENCE_DATE, current_dept_years) if rotation_count > 0 else pd.NaT

    # --- contract ---------------------------------------------------------
    if is_officer:
        contract_length = random.choices([3, 5, 7, 10], weights=[0.2, 0.3, 0.2, 0.3])[0]
    else:
        contract_length = random.choices([3, 5, 7], weights=[0.4, 0.4, 0.2])[0]
    time_into_contract = round(random.uniform(0, contract_length), 2)
    contract_start = years_before(REFERENCE_DATE, time_into_contract)
    contract_end = date(contract_start.year + contract_length, contract_start.month, contract_start.day) \
        if not (contract_start.month == 2 and contract_start.day == 29) \
        else date(contract_start.year + contract_length, 2, 28)

    first, last, father = make_full_name(gender)
    fin_code = make_fin_code()
    id_card_number = make_id_card_number()
    has_driving_license = random.random() < 0.78
    driving_license_number = make_driving_license_number() if has_driving_license else None

    return {
        "person_id": person_id,
        "first_name": first,
        "last_name": last,
        "father_name": father,
        "gender": gender,
        "fin_code": fin_code,
        "id_card_number": id_card_number,
        "military_ticket_number": None,  # assigned later for cross-person uniqueness
        "has_driving_license": has_driving_license,
        "driving_license_number": driving_license_number,
        "birth_date": birth_date,
        "age": age,
        "home_region": random.choice(AZ_REGIONS),
        "education_level": education_level,
        "university_admission_year": admission_year,
        "university_graduation_year": graduation_year,
        "rank_group": rank_group,
        "rank": rank,
        "specialization": leadership_role if is_leadership else specialization,
        "is_leadership": is_leadership,
        "officer_commissioning_source": commissioning_source,
        "military_academy_type": military_academy_type,
        "years_as_enlisted_before_commission": years_as_enlisted,
        "prior_enlisted_specialization": prior_enlisted_specialization,
        "department": department,
        "total_military_service_years": total_service_years,
        "uav_service_years": uav_service_years,
        "current_department_years": current_dept_years,
        "rotation_count": rotation_count,
        "last_rotation_date": last_rotation_date,
        "contract_start_date": contract_start,
        "contract_end_date": contract_end,
        "contract_length_years": contract_length,
        "pua_course_cohort": random.randint(1, 5),
    }


def generate_department(department):
    rows = []

    # --- Leadership (5 total): 4 officer leads + 1 gizir (technical) lead --
    for i, role in enumerate(LEADERSHIP_ROLES):
        gender = random.choices(["M", "F"], weights=[0.92, 0.08])[0]
        if role == "Technical Service Lead":
            rank, staj = sample_rank_and_service(LEADERSHIP_TECH_LEAD_RANK_WEIGHTS, WARRANT_RANK_RANGES)
            rows.append(("Warrant Officer", rank, staj, None, True, role, gender))
        else:
            weights = LEADERSHIP_COMMANDER_RANK_WEIGHTS if role == "Department Commander" \
                else LEADERSHIP_OTHER_RANK_WEIGHTS
            rank, staj = sample_rank_and_service(weights, OFFICER_RANK_RANGES)
            rows.append(("Officer", rank, staj, None, True, role, gender))

    # --- Operations-officer pool (20): mostly Operations Officer, a few
    #     Flight-Control / Training-Standardization officers ------------
    op_specs = (["Operations Officer"] * 14 + ["Flight Control Officer"] * 3
                + ["Training & Standardization Officer"] * 3)
    for spec in op_specs:
        rank, staj = sample_rank_and_service(REGULAR_OFFICER_RANK_WEIGHTS, OFFICER_RANK_RANGES)
        gender = random.choices(["M", "F"], weights=[0.92, 0.08])[0]
        rows.append(("Officer", rank, staj, spec, False, None, gender))

    # --- Pilot-operators (20) --------------------------------------------
    for _ in range(DEPT_COMPOSITION["pilot_operator"]):
        rank, staj = sample_rank_and_service(REGULAR_OFFICER_RANK_WEIGHTS, OFFICER_RANK_RANGES)
        gender = random.choices(["M", "F"], weights=[0.95, 0.05])[0]
        rows.append(("Officer", rank, staj, "Pilot-Operator", False, None, gender))

    # --- UAV operators (20, warrant) --------------------------------------
    for _ in range(DEPT_COMPOSITION["uav_operator"]):
        rank, staj = sample_rank_and_service(REGULAR_WARRANT_RANK_WEIGHTS, WARRANT_RANK_RANGES)
        gender = random.choices(["M", "F"], weights=[0.9, 0.1])[0]
        rows.append(("Warrant Officer", rank, staj, "UAV Operator", False, None, gender))

    # --- Technical pool (40, warrant): heyət / xidmət / təmir ------------
    tech_specs = (["Technical Staff"] * 20 + ["Technical Service"] * 12
                  + ["Repair Specialist"] * 8)
    for spec in tech_specs:
        rank, staj = sample_rank_and_service(REGULAR_WARRANT_RANK_WEIGHTS, WARRANT_RANK_RANGES)
        gender = random.choices(["M", "F"], weights=[0.85, 0.15])[0]
        rows.append(("Warrant Officer", rank, staj, spec, False, None, gender))

    return rows


def assign_person_ids(rows):
    """Assign IDs of the form AO<YY><NNN> (officers) / G<YY><NNN> (warrant
    officers), where YY = last 2 digits of the year their total military
    service started, and NNN is a random 3-digit number unique within that
    prefix+year bucket (so no collisions). Also assigns a unique
    military_ticket_number per service-start-year bucket for the same
    collision-avoidance reason."""
    id_buckets = {}
    ticket_buckets = {}
    for i, r in enumerate(rows):
        prefix = "AO" if r["rank_group"] == "Officer" else "G"
        start_year = REFERENCE_DATE.year - round(r["total_military_service_years"])
        yy = f"{start_year % 100:02d}"
        id_buckets.setdefault((prefix, yy), []).append(i)
        ticket_buckets.setdefault(yy, []).append(i)

    for (prefix, yy), idxs in id_buckets.items():
        nums = random.sample(range(1000), len(idxs))
        for idx, num in zip(idxs, nums):
            rows[idx]["person_id"] = f"{prefix}{yy}{num:03d}"

    for yy, idxs in ticket_buckets.items():
        nums = random.sample(range(10000), len(idxs))
        for idx, num in zip(idxs, nums):
            rows[idx]["military_ticket_number"] = f"HB{yy}{num:04d}"
    return rows


def main():
    all_rows = []
    for department in DEPARTMENTS:
        for rank_group, rank, staj, spec, is_lead, lead_role, gender in generate_department(department):
            row = build_person_row(None, department, rank_group, rank, staj,
                                    spec, is_lead, lead_role, gender)
            all_rows.append(row)

    all_rows = assign_person_ids(all_rows)

    # --- Manual override: two named "featured top performers" ------------
    captain_idxs = [i for i, r in enumerate(all_rows) if r["rank"] == "Captain"]
    if len(captain_idxs) >= 2:
        i1, i2 = captain_idxs[0], captain_idxs[1]
        all_rows[i1]["first_name"], all_rows[i1]["last_name"], all_rows[i1]["father_name"] = \
            "Adil", "Yaqubov", "Azər oğlu"
        all_rows[i2]["first_name"], all_rows[i2]["last_name"], all_rows[i2]["father_name"] = \
            "Osman", "Qurbanov", "Şəmsəddin oğlu"

    personal_df = pd.DataFrame(all_rows)
    # person_id should read first for readability
    cols = ["person_id"] + [c for c in personal_df.columns if c != "person_id"]
    personal_df = personal_df[cols]

    # ---------------- Rank History (one row per person) --------------------
    history_rows = []
    for _, r in personal_df.iterrows():
        ranks = OFFICER_RANKS if r["rank_group"] == "Officer" else WARRANT_RANKS
        ranges = OFFICER_RANK_RANGES if r["rank_group"] == "Officer" else WARRANT_RANK_RANGES
        idx = ranks.index(r["rank"])
        lo_current, _ = ranges[r["rank"]]
        years_since_promotion = round(r["total_military_service_years"] - lo_current, 2)
        current_rank_date = years_before(REFERENCE_DATE, years_since_promotion)

        if idx == 0:
            previous_rank, previous_rank_date = None, pd.NaT
        else:
            previous_rank = ranks[idx - 1]
            lo_prev, _ = ranges[previous_rank]
            years_since_prev = round(r["total_military_service_years"] - lo_prev, 2)
            previous_rank_date = years_before(REFERENCE_DATE, years_since_prev)

        history_rows.append({
            "person_id": r["person_id"],
            "current_rank": r["rank"],
            "current_rank_date": current_rank_date,
            "previous_rank": previous_rank,
            "previous_rank_date": previous_rank_date,
            "current_rank_tenure_years": years_since_promotion,
            "years_since_last_promotion": years_since_promotion,
        })

    rank_history_df = pd.DataFrame(history_rows)

    personal_df.to_csv("/home/claude/personal.csv", index=False)
    rank_history_df.to_csv("/home/claude/rank_history.csv", index=False)

    print(f"Total personnel: {len(personal_df)}")
    print(personal_df["department"].value_counts())
    print()
    print(personal_df["rank_group"].value_counts())
    print()
    print(personal_df.groupby("rank_group")["rank"].value_counts())
    print()
    print("Sample rows:")
    print(personal_df.head(3).to_string())
    print()
    print(rank_history_df.head(3).to_string())


if __name__ == "__main__":
    main()
