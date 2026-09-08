/* ==========================================================================
Database Load Issues (follow if receiving permission denied when running the
COPY commands below)

If you get: 'could not open file "[path]/personal.csv" for reading: Permission denied.'

1. Open pgAdmin
2. In Object Explorer (left-hand pane), navigate to the uav_analytics database
3. Right-click uav_analytics and select 'PSQL Tool' (opens a terminal)
4. Get the absolute file path of your data/ folder
    - In VS Code, right-click a CSV file and select 'Copy Path'
5. Paste the \copy commands below into the PSQL Tool, with YOUR correct path,
   e.g.:

\copy mission_profile FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/mission_profile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

========================================================================== */

-- If running this whole file directly with `psql -f 3_load_data.sql`, edit the
-- path below first (find-and-replace /Users/islamrehim/Downloads/uav-analytics-portfolio_1 with your real absolute path).

\copy mission_profile(department, target_sector, climb_hours, transit_to_target_hours, transit_return_hours, descent_hours, max_flight_duration_hours, total_transit_hours, target_dwell_hours, mission_effectiveness_pct) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/mission_profile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy personal(person_id, first_name, last_name, father_name, gender, fin_code, id_card_number, military_ticket_number, has_driving_license, driving_license_number, birth_date, age, home_region, education_level, university_admission_year, university_graduation_year, rank_group, rank, specialization, is_leadership, officer_commissioning_source, military_academy_type, years_as_enlisted_before_commission, prior_enlisted_specialization, department, total_military_service_years, uav_service_years, current_department_years, rotation_count, last_rotation_date, contract_start_date, contract_end_date, contract_length_years, pua_course_cohort) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/personal.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy aircraft(aircraft_id, department, model, in_service_date, base_condition_score) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/aircraft.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy rank_history(person_id, current_rank, current_rank_date, previous_rank, previous_rank_date, current_rank_tenure_years, years_since_last_promotion) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/rank_history.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy previous_service(person_id, previous_branch, years_in_previous_branch) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/previous_service.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy rank_delay_analysis(person_id, transferred_from_other_branch, rank_delayed, delay_years, department, rank) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/rank_delay_analysis.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy certifications(person_id, english_certified, russian_certified, other_language_certified, other_language_name, nato_training, foreign_course, instructor_certified) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/certifications.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy fitness_standards(age_group, age_range, score, pullups_required, run_minutes_required, is_passing) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/fitness_standards.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy physical_fitness(person_id, year, age_group, pullups_count, run_3km_minutes, pullup_score, run_score, fitness_score, result) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/physical_fitness.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy tactical_training(person_id, training_name, level, year, role, result, score) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/tactical_training.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy discipline_records(record_id, person_id, department, year, month, record_type, severity, reason) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/discipline_records.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy mission_log(mission_id, department, year, month, mission_date, planned_duration_hours, status, cancellation_reason, dominant_weather, avg_temperature_c, person_id, role_on_mission, shift_hours, hours_category) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/mission_log.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy flight_operations(person_id, department, year, month, planned_missions, completed_missions, cancelled_missions, flight_hours_real, flight_hours_training, flight_hours_combat, flight_hours_test, flight_hours_simulator, avg_temperature_c, avg_wind_speed_kmh, dominant_weather, primary_cancellation_reason) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/flight_operations.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy shooting_performance(shot_id, person_id, department, shot_date, shot_sequence_number, is_first_shot, shot_type, outcome) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/shooting_performance.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy standardization_exams(person_id, department, exam_year, standardization_score, flight_clearance, retake_required, retake_score, final_clearance_status, evaluator_id) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/standardization_exams.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy fuel_consumption(department, year, total_flight_hours_real, total_flight_hours_simulator, primary_uav_model, avg_technical_condition_score, fuel_burn_rate_l_per_hour, total_fuel_liters, estimated_flying_days) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/fuel_consumption.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy flight_safety(incident_id, mission_id, person_id, department, incident_date, incident_type, cause, severity_score, investigation_outcome) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/flight_safety.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy medals(medal_id, person_id, department, medal_type, award_date, reason) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/medals.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy risk_score(person_id, risk_score, risk_flight, risk_exam, risk_shoot, risk_disc_safety, risk_training, department, rank, specialization) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/risk_score.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy aircraft_monthly_maintenance(aircraft_id, department, year, month, maintenance_hours, technician_id, effective_condition_score) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/aircraft_monthly_maintenance.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy mission_technical_log(mission_id, aircraft_id, department, year, month, mission_date, aircraft_age_years, planned_duration_hours, actual_duration_hours, hours_returned_early, pre_flight_check_minutes, pre_flight_issue_found, post_flight_check_minutes, had_inflight_technical_problem, problem_type, problem_duration_minutes, effective_condition_score) FROM '/Users/islamrehim/Downloads/uav-analytics-portfolio_1/data/mission_technical_log.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');
