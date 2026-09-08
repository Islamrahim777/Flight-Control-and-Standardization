"""
Generates:
  - rank_delay_analysis.csv

For people who transferred into the PUA unit from ANOTHER military branch
(previous_branch is an external branch — not Civilian Sector, not
Internal Promotion), flags whether their next promotion was
administratively delayed (paperwork/re-certification lag common when
switching branches), with a delay_years estimate.

NOTE for later: when the full pipeline is rebuilt, rank_delayed=True
people should show WEAKER flight hours and HIGHER risk scores (per
user's hypothesis) — this table is the join key for that.

Depends on personal.csv, previous_service.csv, rank_history.csv.
Run: python3 generate_rank_delay_analysis.py
"""

import random
import numpy as np
import pandas as pd

random.seed(51)
np.random.seed(51)

EXTERNAL_BRANCHES_EXCLUDE = {"Civilian Sector (Direct Entry)",
                              "Internal Promotion (Former UAV Operator, this unit)"}

P_DELAYED = 0.35  # share of external-branch transfers who experienced a delay


def main():
    personal = pd.read_csv("/home/claude/personal.csv")
    prev_service = pd.read_csv("/home/claude/previous_service.csv")
    rank_hist = pd.read_csv("/home/claude/rank_history.csv")

    df = personal[["person_id", "department", "rank_group", "rank",
                   "total_military_service_years"]].merge(
        prev_service[["person_id", "previous_branch", "years_in_previous_branch"]],
        on="person_id").merge(
        rank_hist[["person_id", "current_rank_tenure_years"]], on="person_id")

    df["transferred_from_other_branch"] = ~df["previous_branch"].isin(EXTERNAL_BRANCHES_EXCLUDE)

    rows = []
    for _, r in df.iterrows():
        if not r["transferred_from_other_branch"]:
            rows.append({"person_id": r["person_id"], "transferred_from_other_branch": False,
                         "rank_delayed": None, "delay_years": None})
            continue
        delayed = random.random() < P_DELAYED
        delay_years = round(random.uniform(1, 3), 1) if delayed else 0.0
        rows.append({
            "person_id": r["person_id"],
            "transferred_from_other_branch": True,
            "rank_delayed": delayed,
            "delay_years": delay_years,
        })

    out = pd.DataFrame(rows).merge(
        personal[["person_id", "department", "rank"]], on="person_id")
    out.to_csv("/home/claude/rank_delay_analysis.csv", index=False)

    transferred = out[out.transferred_from_other_branch == True]
    print(f"Transferred from another branch: {len(transferred)}")
    print(f"Of those, rank-delayed: {transferred.rank_delayed.sum()} "
          f"({transferred.rank_delayed.mean():.1%})")
    print()
    print("By department:")
    print(transferred.groupby("department")["rank_delayed"].mean().round(2))


if __name__ == "__main__":
    main()
