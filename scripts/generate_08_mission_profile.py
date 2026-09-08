"""
Generates:
  - mission_profile.csv   (Table 12: Mission Profile) — one row per department.

Pattern from the user's own example: every department spends the same
2h climbing to altitude and 1h descending; only the transit time to/from
the target sector differs, growing by 0.5h (each way) per department as
you go Alpha -> Echo (i.e. Echo covers the farthest sector). Dwell time
over the target = max flight duration minus all transit legs.

No dependencies — standalone table.
Run: python3 generate_08_mission_profile.py
"""

import pandas as pd
from uav_dataset_config import DEPARTMENTS

CLIMB_HOURS = 2.0
DESCENT_HOURS = 1.0
MAX_FLIGHT_HOURS = 15.0

SECTOR_NAMES = {
    "Alpha": "Northern Sector (near base)",
    "Beta": "Eastern Sector",
    "Delta": "Central Sector",
    "Gamma": "Southern Sector",
    "Sigma": "Western Sector (far border)",
}


def main():
    rows = []
    for i, dept in enumerate(DEPARTMENTS):
        one_way_transit = 0.5 + 0.5 * i          # Alpha=0.5h ... Echo=2.5h
        transit_total = one_way_transit * 2
        non_dwell = CLIMB_HOURS + DESCENT_HOURS + transit_total
        dwell_hours = MAX_FLIGHT_HOURS - non_dwell
        effectiveness_pct = round(dwell_hours / MAX_FLIGHT_HOURS * 100, 1)

        rows.append({
            "department": dept,
            "target_sector": SECTOR_NAMES[dept],
            "climb_hours": CLIMB_HOURS,
            "transit_to_target_hours": one_way_transit,
            "transit_return_hours": one_way_transit,
            "descent_hours": DESCENT_HOURS,
            "max_flight_duration_hours": MAX_FLIGHT_HOURS,
            "total_transit_hours": transit_total,
            "target_dwell_hours": dwell_hours,
            "mission_effectiveness_pct": effectiveness_pct,
        })

    df = pd.DataFrame(rows)
    df.to_csv("/home/claude/mission_profile.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
