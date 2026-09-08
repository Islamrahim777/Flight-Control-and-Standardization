"""
Final analysis layer — pulls everything together into:
  1) A printed "key findings" report (medians + correlations)
  2) A handful of clean, dashboard-ready CSVs for Tableau/Power BI:
       - dash_department_scorecard.csv
       - dash_medal_mismatch.csv
       - dash_monthly_flight_trend.csv
       - dash_rank_flight_trend.csv
       - dash_risk_distribution.csv

Run: python3 generate_12_final_analysis.py
"""

import numpy as np
import pandas as pd

pd.set_option("display.width", 120)


def main():
    personal = pd.read_csv("/home/claude/personal.csv")
    flight = pd.read_csv("/home/claude/flight_operations.csv")
    shots = pd.read_csv("/home/claude/shooting_performance.csv")
    fuel = pd.read_csv("/home/claude/fuel_consumption.csv")
    medals = pd.read_csv("/home/claude/medals.csv")
    risk = pd.read_csv("/home/claude/risk_score.csv")
    fitness = pd.read_csv("/home/claude/physical_fitness.csv")
    discipline = pd.read_csv("/home/claude/discipline_records.csv")
    tactical = pd.read_csv("/home/claude/tactical_training.csv")

    # ---------- per-person rollups used throughout -------------------------
    succ = shots.groupby("person_id")["outcome"].apply(lambda s: (s == "Successful").mean())
    hours = flight.groupby("person_id")["flight_hours_real"].sum()
    medal_ct = medals.groupby("person_id").size()

    roll = personal[["person_id", "department", "rank", "rank_group", "is_leadership"]].copy()
    roll["success_rate"] = roll.person_id.map(succ)
    roll["total_flight_hours"] = roll.person_id.map(hours).fillna(0)
    roll["medal_count"] = roll.person_id.map(medal_ct).fillna(0).astype(int)
    roll = roll.merge(risk[["person_id", "risk_score"]], on="person_id", how="left")

    # =========================================================================
    # 1) MEDIAN PERFORMANCE BY DEPARTMENT
    # =========================================================================
    median_tbl = roll.groupby("department").agg(
        median_flight_hours=("total_flight_hours", "median"),
        median_success_rate=("success_rate", "median"),
        median_risk_score=("risk_score", "median"),
        median_medals=("medal_count", "median"),
    ).round(3)
    print("=" * 70)
    print("MEDIAN PERFORMANCE BY DEPARTMENT")
    print("=" * 70)
    print(median_tbl)

    # =========================================================================
    # 2) CORRELATION ANALYSIS
    # =========================================================================
    print("\n" + "=" * 70)
    print("CORRELATION ANALYSIS")
    print("=" * 70)
    print(f"medal_count vs success_rate      : {roll['medal_count'].corr(roll['success_rate']):.3f}")
    print(f"medal_count vs total_flight_hours : {roll['medal_count'].corr(roll['total_flight_hours']):.3f}")
    print(f"medal_count vs risk_score         : {roll['medal_count'].corr(roll['risk_score']):.3f}")

    officer_rank_order = ["Lieutenant", "Senior Lieutenant", "Captain", "Major", "Lieutenant Colonel"]
    off = roll[roll.rank_group == "Officer"].copy()
    off["rank_level"] = off["rank"].map({r: i for i, r in enumerate(officer_rank_order)})
    print(f"rank_level vs total_flight_hours (officers) : {off['rank_level'].corr(off['total_flight_hours']):.3f}")

    fit_avg = fitness.groupby("person_id")["fitness_score"].mean()
    neg_disc = (discipline[discipline.record_type.isin(["Reprimand", "Warning"])]
                .groupby("person_id").size())
    disc_df = pd.DataFrame({"fitness": fit_avg})
    disc_df["neg_records"] = disc_df.index.map(neg_disc).fillna(0)
    n_train = tactical.groupby("person_id").size()
    disc_df["n_trainings"] = disc_df.index.map(n_train).fillna(0)
    print(f"fitness vs discipline records                : {disc_df['fitness'].corr(disc_df['neg_records']):.3f}")
    print(f"tactical trainings vs discipline records      : {disc_df['n_trainings'].corr(disc_df['neg_records']):.3f}")

    # =========================================================================
    # 3) DASHBOARD EXPORTS
    # =========================================================================
    dept_scorecard = fuel.groupby("department").agg(
        total_flight_hours=("total_flight_hours_real", "sum"),
        avg_fuel_burn_l_per_hour=("fuel_burn_rate_l_per_hour", "mean"),
        avg_tech_condition=("avg_technical_condition_score", "mean"),
    ).round(2)
    dept_scorecard = dept_scorecard.join(
        roll.groupby("department").agg(
            avg_success_rate=("success_rate", "mean"),
            avg_medals=("medal_count", "mean"),
            avg_risk_score=("risk_score", "mean"),
        ).round(3)
    ).reset_index()
    dept_scorecard.to_csv("/home/claude/dash_department_scorecard.csv", index=False)

    mismatch = roll.dropna(subset=["success_rate"])[
        ["person_id", "department", "rank", "success_rate", "total_flight_hours",
         "medal_count", "risk_score"]
    ]
    mismatch.to_csv("/home/claude/dash_medal_mismatch.csv", index=False)

    monthly = flight.groupby("month")["flight_hours_real"].mean().round(2).reset_index()
    monthly.columns = ["month", "avg_flight_hours"]
    monthly.to_csv("/home/claude/dash_monthly_flight_trend.csv", index=False)

    last12 = flight[((flight.year == 2025) & (flight.month > 6)) | ((flight.year == 2026) & (flight.month <= 6))]
    rank_flight = (last12.merge(personal[["person_id", "rank", "rank_group"]], on="person_id")
                   .groupby(["rank_group", "rank"])["flight_hours_real"].sum()
                   .reset_index().rename(columns={"flight_hours_real": "total_hours_last_12mo"}))
    rank_flight.to_csv("/home/claude/dash_rank_flight_trend.csv", index=False)

    risk_dist = risk[["person_id", "department", "rank", "specialization", "risk_score"]]
    risk_dist.to_csv("/home/claude/dash_risk_distribution.csv", index=False)

    print("\n" + "=" * 70)
    print("DASHBOARD FILES WRITTEN")
    print("=" * 70)
    for f in ["dash_department_scorecard.csv", "dash_medal_mismatch.csv",
              "dash_monthly_flight_trend.csv", "dash_rank_flight_trend.csv",
              "dash_risk_distribution.csv"]:
        print(" -", f)


if __name__ == "__main__":
    main()
