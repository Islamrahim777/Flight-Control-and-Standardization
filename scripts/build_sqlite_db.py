"""
Builds uav_analytics.db from scratch — the FULL, current schema
(post mission-crew-model rewrite): 18 tables, all foreign keys enforced.

Run: python3 build_sqlite_db.py
"""

import os
import sqlite3
import pandas as pd

DB_PATH = "/home/claude/uav_analytics.db"
DATA_DIR = "/home/claude"

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE mission_profile (
    department TEXT PRIMARY KEY,
    target_sector TEXT,
    climb_hours REAL,
    transit_to_target_hours REAL,
    transit_return_hours REAL,
    descent_hours REAL,
    max_flight_duration_hours REAL,
    total_transit_hours REAL,
    target_dwell_hours REAL,
    mission_effectiveness_pct REAL
);

CREATE TABLE personal (
    person_id TEXT PRIMARY KEY,
    first_name TEXT, last_name TEXT, father_name TEXT, gender TEXT,
    fin_code TEXT, id_card_number TEXT, military_ticket_number TEXT,
    has_driving_license INTEGER, driving_license_number TEXT,
    birth_date TEXT, age INTEGER, home_region TEXT,
    education_level TEXT, university_admission_year INTEGER, university_graduation_year INTEGER,
    rank_group TEXT, rank TEXT, specialization TEXT, is_leadership INTEGER,
    officer_commissioning_source TEXT, military_academy_type TEXT,
    years_as_enlisted_before_commission REAL, prior_enlisted_specialization TEXT,
    department TEXT,
    total_military_service_years REAL, uav_service_years REAL, current_department_years REAL,
    rotation_count INTEGER, last_rotation_date TEXT,
    contract_start_date TEXT, contract_end_date TEXT, contract_length_years INTEGER,
    pua_course_cohort INTEGER,
    FOREIGN KEY (department) REFERENCES mission_profile(department)
);

CREATE TABLE rank_history (
    person_id TEXT PRIMARY KEY,
    current_rank TEXT, current_rank_date TEXT, previous_rank TEXT, previous_rank_date TEXT,
    current_rank_tenure_years REAL, years_since_last_promotion REAL,
    FOREIGN KEY (person_id) REFERENCES personal(person_id)
);

CREATE TABLE previous_service (
    person_id TEXT PRIMARY KEY,
    previous_branch TEXT, years_in_previous_branch REAL,
    FOREIGN KEY (person_id) REFERENCES personal(person_id)
);

CREATE TABLE rank_delay_analysis (
    person_id TEXT PRIMARY KEY,
    transferred_from_other_branch INTEGER,
    rank_delayed INTEGER,
    delay_years REAL,
    department TEXT,
    rank TEXT,
    FOREIGN KEY (person_id) REFERENCES personal(person_id)
);

CREATE TABLE certifications (
    person_id TEXT PRIMARY KEY,
    english_certified INTEGER, russian_certified INTEGER, other_language_certified INTEGER,
    other_language_name TEXT, nato_training INTEGER, foreign_course INTEGER, instructor_certified INTEGER,
    FOREIGN KEY (person_id) REFERENCES personal(person_id)
);

CREATE TABLE fitness_standards (
    age_group INTEGER,
    age_range TEXT,
    score INTEGER,
    pullups_required INTEGER,
    run_minutes_required REAL,
    is_passing INTEGER,
    PRIMARY KEY (age_group, score)
);

CREATE TABLE physical_fitness (
    person_id TEXT, year INTEGER, age_group INTEGER,
    pullups_count INTEGER, run_3km_minutes REAL,
    pullup_score REAL, run_score REAL, fitness_score REAL, result TEXT,
    PRIMARY KEY (person_id, year),
    FOREIGN KEY (person_id) REFERENCES personal(person_id)
);

CREATE TABLE tactical_training (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id TEXT, training_name TEXT, level TEXT, year INTEGER, role TEXT, result TEXT, score REAL,
    FOREIGN KEY (person_id) REFERENCES personal(person_id)
);

CREATE TABLE discipline_records (
    record_id TEXT PRIMARY KEY,
    person_id TEXT, department TEXT, year INTEGER, month INTEGER,
    record_type TEXT, severity TEXT, reason TEXT,
    FOREIGN KEY (person_id) REFERENCES personal(person_id),
    FOREIGN KEY (department) REFERENCES mission_profile(department)
);

CREATE TABLE mission_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id TEXT, department TEXT, year INTEGER, month INTEGER, mission_date TEXT,
    planned_duration_hours REAL, status TEXT, cancellation_reason TEXT,
    dominant_weather TEXT, avg_temperature_c REAL,
    person_id TEXT, role_on_mission TEXT, shift_hours REAL, hours_category TEXT,
    FOREIGN KEY (department) REFERENCES mission_profile(department),
    FOREIGN KEY (person_id) REFERENCES personal(person_id)
);

CREATE TABLE flight_operations (
    person_id TEXT, department TEXT, year INTEGER, month INTEGER,
    planned_missions INTEGER, completed_missions INTEGER, cancelled_missions INTEGER,
    flight_hours_real REAL, flight_hours_training REAL, flight_hours_combat REAL, flight_hours_test REAL,
    flight_hours_simulator REAL, avg_temperature_c REAL, avg_wind_speed_kmh REAL,
    dominant_weather TEXT, primary_cancellation_reason TEXT,
    PRIMARY KEY (person_id, year, month),
    FOREIGN KEY (person_id) REFERENCES personal(person_id),
    FOREIGN KEY (department) REFERENCES mission_profile(department)
);

CREATE TABLE shooting_performance (
    shot_id TEXT PRIMARY KEY,
    person_id TEXT, department TEXT, shot_date TEXT, shot_sequence_number INTEGER,
    is_first_shot INTEGER, shot_type TEXT, outcome TEXT,
    FOREIGN KEY (person_id) REFERENCES personal(person_id),
    FOREIGN KEY (department) REFERENCES mission_profile(department)
);

CREATE TABLE standardization_exams (
    person_id TEXT, department TEXT, exam_year INTEGER,
    standardization_score REAL, flight_clearance TEXT, retake_required INTEGER, retake_score REAL,
    final_clearance_status TEXT, evaluator_id TEXT,
    PRIMARY KEY (person_id, exam_year),
    FOREIGN KEY (person_id) REFERENCES personal(person_id),
    FOREIGN KEY (evaluator_id) REFERENCES personal(person_id),
    FOREIGN KEY (department) REFERENCES mission_profile(department)
);

CREATE TABLE fuel_consumption (
    department TEXT, year INTEGER,
    total_flight_hours_real REAL, total_flight_hours_simulator REAL, primary_uav_model TEXT,
    avg_technical_condition_score REAL, fuel_burn_rate_l_per_hour REAL, total_fuel_liters REAL,
    estimated_flying_days INTEGER,
    PRIMARY KEY (department, year),
    FOREIGN KEY (department) REFERENCES mission_profile(department)
);

CREATE TABLE flight_safety (
    incident_id TEXT PRIMARY KEY,
    mission_id TEXT, person_id TEXT, department TEXT, incident_date TEXT, incident_type TEXT, cause TEXT,
    severity_score INTEGER, investigation_outcome TEXT,
    FOREIGN KEY (person_id) REFERENCES personal(person_id),
    FOREIGN KEY (department) REFERENCES mission_profile(department)
);

CREATE TABLE medals (
    medal_id TEXT PRIMARY KEY,
    person_id TEXT, department TEXT, medal_type TEXT, award_date TEXT, reason TEXT,
    FOREIGN KEY (person_id) REFERENCES personal(person_id),
    FOREIGN KEY (department) REFERENCES mission_profile(department)
);

CREATE TABLE aircraft (
    aircraft_id TEXT PRIMARY KEY,
    department TEXT, model TEXT, in_service_date TEXT, base_condition_score REAL,
    FOREIGN KEY (department) REFERENCES mission_profile(department)
);

CREATE TABLE aircraft_monthly_maintenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aircraft_id TEXT, department TEXT, year INTEGER, month INTEGER,
    maintenance_hours REAL, technician_id TEXT, effective_condition_score REAL,
    FOREIGN KEY (aircraft_id) REFERENCES aircraft(aircraft_id),
    FOREIGN KEY (technician_id) REFERENCES personal(person_id)
);

CREATE TABLE mission_technical_log (
    mission_id TEXT PRIMARY KEY,
    aircraft_id TEXT, department TEXT, year INTEGER, month INTEGER, mission_date TEXT,
    aircraft_age_years INTEGER,
    planned_duration_hours REAL, actual_duration_hours REAL, hours_returned_early REAL,
    pre_flight_check_minutes REAL, pre_flight_issue_found INTEGER,
    post_flight_check_minutes REAL,
    had_inflight_technical_problem INTEGER, problem_type TEXT, problem_duration_minutes REAL,
    effective_condition_score REAL,
    FOREIGN KEY (aircraft_id) REFERENCES aircraft(aircraft_id)
);

CREATE TABLE risk_score (
    person_id TEXT PRIMARY KEY,
    risk_score REAL, risk_flight REAL, risk_exam REAL, risk_shoot REAL,
    risk_disc_safety REAL, risk_training REAL,
    department TEXT, rank TEXT, specialization TEXT,
    FOREIGN KEY (person_id) REFERENCES personal(person_id)
);
"""

LOAD_ORDER = [
    ("mission_profile.csv", "mission_profile"),
    ("personal.csv", "personal"),
    ("rank_history.csv", "rank_history"),
    ("previous_service.csv", "previous_service"),
    ("rank_delay_analysis.csv", "rank_delay_analysis"),
    ("certifications.csv", "certifications"),
    ("fitness_standards.csv", "fitness_standards"),
    ("physical_fitness.csv", "physical_fitness"),
    ("tactical_training.csv", "tactical_training"),
    ("discipline_records.csv", "discipline_records"),
    ("mission_log.csv", "mission_log"),
    ("aircraft.csv", "aircraft"),
    ("aircraft_monthly_maintenance.csv", "aircraft_monthly_maintenance"),
    ("mission_technical_log.csv", "mission_technical_log"),
    ("flight_operations.csv", "flight_operations"),
    ("shooting_performance.csv", "shooting_performance"),
    ("standardization_exams.csv", "standardization_exams"),
    ("fuel_consumption.csv", "fuel_consumption"),
    ("flight_safety.csv", "flight_safety"),
    ("medals.csv", "medals"),
    ("risk_score.csv", "risk_score"),
]


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    for csv_name, table in LOAD_ORDER:
        df = pd.read_csv(os.path.join(DATA_DIR, csv_name))
        df.to_sql(table, conn, if_exists="append", index=False)
        print(f"Loaded {len(df):>6} rows -> {table}")

    conn.commit()

    print("\nRow counts per table:")
    for _, table in LOAD_ORDER:
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<24} {n}")

    print("\nForeign-key check (should be empty):")
    fk_issues = conn.execute("PRAGMA foreign_key_check").fetchall()
    print(fk_issues if fk_issues else "  none — all references valid")

    conn.close()
    print(f"\nDatabase written to {DB_PATH}")


if __name__ == "__main__":
    main()
