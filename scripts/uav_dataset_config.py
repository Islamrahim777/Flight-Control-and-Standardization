"""
Shared configuration and reference data for the synthetic UAV unit
HR/operations analytics dataset.

This module is imported by every table-generation script so that all
tables (Personal, Rank History, Previous Service, ... ) stay consistent
with each other (same person IDs, same department structure, same
rank rules).
"""

import random
import numpy as np
import pandas as pd
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# "Today" for the whole synthetic world — the dataset represents a snapshot
# taken near the end of the 2021-2026 period.
REFERENCE_DATE = date(2026, 6, 30)

# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------
DEPARTMENTS = ["Alpha", "Beta", "Delta", "Gamma", "Sigma"]

# Approximate headcount per department per specialization pool.
# 5 (leadership) + 20 (Operations Officer pool) + 20 (Pilot-Operator)
# + 20 (UAV Operator) + 40 (Technical pool) = 105/department -> 525 total
# (matches the "500+, not exactly 600" requirement).
DEPT_COMPOSITION = {
    "leadership": 5,
    "operations_officer_pool": 20,   # includes a few Flight-Control /
                                      # Training-Standardization officers
    "pilot_operator": 20,
    "uav_operator": 20,              # gizir specialization
    "technical_pool": 40,            # gizir specializations
}

# ---------------------------------------------------------------------------
# Ranks
# ---------------------------------------------------------------------------
# (lower_bound_years, upper_bound_years) of TOTAL military service typically
# associated with holding this rank — used both to sample a person's total
# service given their rank, and to back out "years since last promotion"
# (promotion assumed to happen exactly when service crosses lower_bound).
OFFICER_RANKS = ["Lieutenant", "Senior Lieutenant", "Captain", "Major",
                  "Lieutenant Colonel"]
OFFICER_RANK_RANGES = {
    "Lieutenant": (1, 3),
    "Senior Lieutenant": (4, 6),
    "Captain": (7, 11),
    "Major": (12, 15),
    "Lieutenant Colonel": (15, 30),
}
# NOTE (per user rule): Lieutenant Colonel is reserved EXCLUSIVELY for
# Department Commanders. No regular officer or other leadership role
# may hold this rank. Colonel rank removed entirely — Lt Colonel is now
# the top of the ladder.

WARRANT_RANKS = ["Junior Warrant Officer", "Warrant Officer", "Senior Warrant Officer"]
WARRANT_RANK_RANGES = {
    "Junior Warrant Officer": (1, 3),
    "Warrant Officer": (3, 5),
    "Senior Warrant Officer": (5, 20),
}

# Rank distribution for *regular* (non-leadership) officers — skewed junior,
# like a normal military pyramid. Lieutenant Colonel is EXCLUDED here on
# purpose: it may only be held by a Department Commander (see below).
REGULAR_OFFICER_RANK_WEIGHTS = {
    "Lieutenant": 0.35,
    "Senior Lieutenant": 0.30,
    "Captain": 0.24,
    "Major": 0.11,
}
# Department Commander is ALWAYS Lieutenant Colonel (the one and only role
# allowed to hold it) — not a weighted draw.
LEADERSHIP_COMMANDER_RANK_WEIGHTS = {
    "Lieutenant Colonel": 1.0,
}
# Other leadership roles (Chief of Operations, Pilot-Operator Lead,
# Technical Service Lead, Training & Standardization Lead) top out at Major.
LEADERSHIP_OTHER_RANK_WEIGHTS = {
    "Captain": 0.40, "Major": 0.60,
}
REGULAR_WARRANT_RANK_WEIGHTS = {
    "Junior Warrant Officer": 0.30, "Warrant Officer": 0.40, "Senior Warrant Officer": 0.30,
}
# Technical Service Lead is a gizir (warrant) role, skewed senior since it's
# a lead/chief position — per user rule: ALL technical personnel, including
# their lead, are gizirs (no officer oversees pure technical/maintenance work).
LEADERSHIP_TECH_LEAD_RANK_WEIGHTS = {
    "Warrant Officer": 0.35, "Senior Warrant Officer": 0.65,
}

# ---------------------------------------------------------------------------
# Specializations
# ---------------------------------------------------------------------------
OFFICER_SPECIALIZATIONS = [
    "Operations Officer",
    "Pilot-Operator",
    "Flight Control Officer",
    "Training & Standardization Officer",
]
WARRANT_SPECIALIZATIONS = [
    "UAV Operator",
    "Technical Staff",
    "Technical Service",
    "Repair Specialist",
]
LEADERSHIP_ROLES = [
    "Department Commander",
    "Chief of Operations",
    "Pilot-Operator Lead",
    "Technical Service Lead",
    "Training & Standardization Lead",
]

# ---------------------------------------------------------------------------
# Names (synthetic but Azerbaijani-flavored)
# ---------------------------------------------------------------------------
MALE_FIRST_NAMES = [
    "Elvin", "Tural", "Orxan", "Rəşad", "Elnur", "Kamran", "Vüsal", "Anar",
    "Ramin", "Namiq", "Fərid", "Elşən", "Rövşən", "Cavid", "Nicat", "Şahin",
    "Ruslan", "Emin", "Murad", "Vüqar", "Tofiq", "Sənan", "Elçin", "Fuad",
    "Kənan", "İlkin", "Zaur", "Aqşin", "Vaqif", "Ceyhun",
]
FEMALE_FIRST_NAMES = [
    "Aysel", "Nərgiz", "Günel", "Leyla", "Aygün", "Səbinə", "Nigar",
    "Ülviyyə", "Turanə", "Xəyalə", "Röya", "Şəbnəm", "Aytac", "Nərmin", "Vüsalə",
]
SURNAME_ROOTS = [
    "Məmməd", "Əli", "Həsən", "Hüseyn", "Quliy", "Rəhim", "İbrahim", "Vəli",
    "Nəsir", "Kərim", "Şıxəli", "Abbas", "Rüstəm", "Tağı", "Cəfər", "Səfər",
    "Yusif", "Nağı", "Fərəc", "Hacı", "Xəlil", "Musa", "Sultan", "Qara",
]
FATHER_NAME_POOL = MALE_FIRST_NAMES  # patronymic base

AZ_REGIONS = [
    "Bakı", "Gəncə", "Sumqayıt", "Şirvan", "Mingəçevir", "Naxçıvan", "Şəki",
    "Lənkəran", "Quba", "Şamaxı", "Qazax", "Tovuz", "Goranboy", "Ağdam",
    "Zaqatala", "Xaçmaz", "Salyan", "İmişli", "Bərdə", "Yevlax",
]


def make_full_name(gender: str):
    """Return (first_name, last_name, father_name) for the given gender ('M'/'F')."""
    root = random.choice(SURNAME_ROOTS)
    if gender == "M":
        first = random.choice(MALE_FIRST_NAMES)
        last = root + "ov"
        father = random.choice(FATHER_NAME_POOL) + " oğlu"
    else:
        first = random.choice(FEMALE_FIRST_NAMES)
        last = root + "ova"
        father = random.choice(FATHER_NAME_POOL) + " qızı"
    return first, last, father


def sample_rank_and_service(weights: dict, rank_ranges: dict):
    """Pick a rank from a weight dict, then sample total service years
    uniformly within that rank's (lower, upper) range."""
    ranks = list(weights.keys())
    probs = list(weights.values())
    rank = random.choices(ranks, weights=probs, k=1)[0]
    lo, hi = rank_ranges[rank]
    total_service_years = round(random.uniform(lo, hi), 2)
    return rank, total_service_years


def years_before(ref_date: date, years: float) -> date:
    """ref_date minus a (possibly fractional) number of years."""
    return ref_date - timedelta(days=years * 365.25)


FIN_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # avoid ambiguous chars (0/O, 1/I)


def make_fin_code():
    """Synthetic 7-character FIN-style code (NOT a real checksum-valid FIN)."""
    return "".join(random.choices(FIN_CHARS, k=7))


def make_id_card_number():
    """Synthetic ID-card-style number: 2 letters + 7 digits."""
    letters = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=2))
    digits = "".join(random.choices("0123456789", k=7))
    return f"{letters}{digits}"


def make_military_ticket_number(start_year: int):
    """Synthetic military-ticket-style number: HB + 2-digit year + 4 random digits."""
    yy = start_year % 100
    digits = "".join(random.choices("0123456789", k=4))
    return f"HB{yy:02d}{digits}"


def make_driving_license_number():
    """Synthetic driving-license-style number: SV + 7 random digits."""
    digits = "".join(random.choices("0123456789", k=7))
    return f"SV{digits}"
