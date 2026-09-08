"""
Generates:
  - risk_score.csv   (Table 3 in the "derived analysis" layer)

Formula (as agreed): 25% last-12-months flight activity, 25% latest
standardization exam score, 25% shooting failure rate, 20% discipline +
safety-incident record, 5% time since last tactical training.

Each component is turned into a 0-1 "risk" value via PERCENTILE RANK
within the relevant population (robust to outliers, easy to explain).
For people to whom a component genuinely doesn't apply (e.g. technical
staff have no personal flight hours or exam), that component is set to
a NEUTRAL 0.5 instead of being counted as maximum risk — the score is
mainly meant for flight-line personnel, but everyone still gets a
comparable number.

Depends on: personal.csv, flight_operations.csv, standardization_exams.csv,
shooting_performance.csv, discipline_records.csv, flight_safety.csv,
tactical_training.csv.
Run: python3 generate_11_risk_score.py
"""

import numpy as np
import pandas as pd

from uav_dataset_config import REFERENCE_DATE

W_FLIGHT, W_EXAM, W_SHOOT, W_DISC_SAFETY, W_TRAINING = 0.25, 0.25, 0.25, 0.20, 0.05


def pct_rank_risk(series, higher_is_worse=True):
    """Return 0-1 risk via percentile rank. If higher_is_worse, a higher raw
    value -> higher risk; otherwise a higher raw value -> lower risk."""
    r = series.rank(pct=True)
    return r if higher_is_worse else 1 - r


def main():
    personal = pd.read_csv("/home/claude/personal.csv")
    flight = pd.read_csv("/home/claude/flight_operations.csv")
    exams = pd.read_csv("/home/claude/standardization_exams.csv")
    shots = pd.read_csv("/home/claude/shooting_performance.csv")
    discipline = pd.read_csv("/home/claude/discipline_records.csv")
    safety = pd.read_csv("/home/claude/flight_safety.csv")
    tactical = pd.read_csv("/home/claude/tactical_training.csv")

    ref_year, ref_month = REFERENCE_DATE.year, REFERENCE_DATE.month

    # --- 1) Last-12-months flight hours ---------------------------------
    last12 = flight[((flight.year == ref_year) & (flight.month <= ref_month))
                     | ((flight.year == ref_year - 1) & (flight.month > ref_month))]
    hours_12mo = last12.groupby("person_id")["flight_hours_real"].sum()

    # --- 2) Latest standardization score ---------------------------------
    latest_exam = (exams.sort_values("exam_year")
                   .groupby("person_id")["standardization_score"].last())

    # --- 3) Shooting failure rate -----------------------------------------
    fail_rate = shots.groupby("person_id")["outcome"].apply(lambda s: (s == "Failed").mean())

    # --- 4) Discipline + safety incident count ----------------------------
    neg_disc = (discipline[discipline.record_type.isin(["Reprimand", "Warning"])]
                .groupby("person_id").size())
    safety_ct = safety.groupby("person_id").size()
    combined_incidents = neg_disc.add(safety_ct, fill_value=0)

    # --- 5) Years since last tactical training -----------------------------
    last_training_year = tactical.groupby("person_id")["year"].max()

    rows = []
    for _, p in personal.iterrows():
        pid = p["person_id"]
        rows.append({
            "person_id": pid,
            "hours_12mo": hours_12mo.get(pid, np.nan),
            "latest_exam_score": latest_exam.get(pid, np.nan),
            "fail_rate": fail_rate.get(pid, np.nan),
            "incidents": combined_incidents.get(pid, 0),
            "years_since_training": (ref_year - last_training_year.get(pid, ref_year - 6)),
        })
    df = pd.DataFrame(rows)

    # Percentile-rank each component ONLY among people who actually have
    # that metric; missing -> neutral 0.5.
    df["risk_flight"] = np.nan
    mask = df.hours_12mo.notna()
    df.loc[mask, "risk_flight"] = pct_rank_risk(df.loc[mask, "hours_12mo"], higher_is_worse=False)
    df["risk_flight"] = df["risk_flight"].fillna(0.5)

    df["risk_exam"] = np.nan
    mask = df.latest_exam_score.notna()
    df.loc[mask, "risk_exam"] = pct_rank_risk(df.loc[mask, "latest_exam_score"], higher_is_worse=False)
    df["risk_exam"] = df["risk_exam"].fillna(0.5)

    df["risk_shoot"] = np.nan
    mask = df.fail_rate.notna()
    df.loc[mask, "risk_shoot"] = pct_rank_risk(df.loc[mask, "fail_rate"], higher_is_worse=True)
    df["risk_shoot"] = df["risk_shoot"].fillna(0.5)

    df["risk_disc_safety"] = pct_rank_risk(df["incidents"], higher_is_worse=True)

    df["risk_training"] = pct_rank_risk(df["years_since_training"], higher_is_worse=True)

    df["risk_score"] = round(100 * (
        W_FLIGHT * df["risk_flight"] + W_EXAM * df["risk_exam"] + W_SHOOT * df["risk_shoot"]
        + W_DISC_SAFETY * df["risk_disc_safety"] + W_TRAINING * df["risk_training"]
    ), 1)

    out = df[["person_id", "risk_score", "risk_flight", "risk_exam", "risk_shoot",
              "risk_disc_safety", "risk_training"]].merge(
        personal[["person_id", "department", "rank", "specialization"]], on="person_id")
    out.to_csv("/home/claude/risk_score.csv", index=False)

    print(out["risk_score"].describe().round(1))
    print()
    print("Avg risk score by department:")
    print(out.groupby("department")["risk_score"].mean().round(1).sort_values(ascending=False))
    print()
    print("Top 5 highest-risk people:")
    print(out.sort_values("risk_score", ascending=False).head(5)
          [["person_id", "department", "rank", "specialization", "risk_score"]].to_string(index=False))
    print()
    print("Correlation risk_score vs failed safety/discipline incident count:")
    merged_check = out.merge(df[["person_id", "incidents"]], on="person_id")
    print(merged_check["risk_score"].corr(merged_check["incidents"]).round(3))


if __name__ == "__main__":
    main()
