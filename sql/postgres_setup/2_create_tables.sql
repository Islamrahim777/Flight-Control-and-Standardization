-- Create mission_profile table
CREATE TABLE public.mission_profile
(
    department VARCHAR(255),
    target_sector VARCHAR(255),
    climb_hours NUMERIC,
    transit_to_target_hours NUMERIC,
    transit_return_hours NUMERIC,
    descent_hours NUMERIC,
    max_flight_duration_hours NUMERIC,
    total_transit_hours NUMERIC,
    target_dwell_hours NUMERIC,
    mission_effectiveness_pct NUMERIC,
    PRIMARY KEY (department)
);

-- Create personal table
CREATE TABLE public.personal
(
    person_id VARCHAR(255),
    first_name TEXT,
    last_name TEXT,
    father_name TEXT,
    gender VARCHAR(255),
    fin_code TEXT,
    id_card_number TEXT,
    military_ticket_number TEXT,
    has_driving_license BOOLEAN,
    driving_license_number TEXT,
    birth_date DATE,
    age INT,
    home_region VARCHAR(255),
    education_level VARCHAR(255),
    university_admission_year INT,
    university_graduation_year INT,
    rank_group VARCHAR(255),
    rank VARCHAR(255),
    specialization VARCHAR(255),
    is_leadership BOOLEAN,
    officer_commissioning_source VARCHAR(255),
    military_academy_type VARCHAR(255),
    years_as_enlisted_before_commission NUMERIC,
    prior_enlisted_specialization VARCHAR(255),
    department VARCHAR(255),
    FOREIGN KEY (department) REFERENCES public.mission_profile (department),
    total_military_service_years NUMERIC,
    uav_service_years NUMERIC,
    current_department_years NUMERIC,
    rotation_count INT,
    last_rotation_date DATE,
    contract_start_date DATE,
    contract_end_date DATE,
    contract_length_years INT,
    pua_course_cohort INT,
    PRIMARY KEY (person_id)
);

-- Create aircraft table
CREATE TABLE public.aircraft
(
    aircraft_id VARCHAR(255),
    department VARCHAR(255),
    FOREIGN KEY (department) REFERENCES public.mission_profile (department),
    model VARCHAR(255),
    in_service_date DATE,
    base_condition_score NUMERIC,
    PRIMARY KEY (aircraft_id)
);

-- Create rank_history table
CREATE TABLE public.rank_history
(
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    current_rank TEXT,
    current_rank_date DATE,
    previous_rank TEXT,
    previous_rank_date DATE,
    current_rank_tenure_years NUMERIC,
    years_since_last_promotion NUMERIC,
    PRIMARY KEY (person_id)
);

-- Create previous_service table
CREATE TABLE public.previous_service
(
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    previous_branch VARCHAR(255),
    years_in_previous_branch NUMERIC,
    PRIMARY KEY (person_id)
);

-- Create rank_delay_analysis table
CREATE TABLE public.rank_delay_analysis
(
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    transferred_from_other_branch BOOLEAN,
    rank_delayed TEXT,
    delay_years NUMERIC,
    department VARCHAR(255),
    rank VARCHAR(255),
    PRIMARY KEY (person_id)
);

-- Create certifications table
CREATE TABLE public.certifications
(
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    english_certified BOOLEAN,
    russian_certified BOOLEAN,
    other_language_certified BOOLEAN,
    other_language_name VARCHAR(255),
    nato_training BOOLEAN,
    foreign_course BOOLEAN,
    instructor_certified BOOLEAN,
    PRIMARY KEY (person_id)
);

-- Create fitness_standards table
CREATE TABLE public.fitness_standards
(
    age_group INT,
    age_range VARCHAR(255),
    score INT,
    pullups_required INT,
    run_minutes_required NUMERIC,
    is_passing BOOLEAN,
    PRIMARY KEY (age_group, score)
);

-- Create physical_fitness table
CREATE TABLE public.physical_fitness
(
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    year INT,
    age_group INT,
    pullups_count INT,
    run_3km_minutes NUMERIC,
    pullup_score NUMERIC,
    run_score NUMERIC,
    fitness_score NUMERIC,
    result VARCHAR(255),
    PRIMARY KEY (person_id, year)
);

-- Create tactical_training table
CREATE TABLE public.tactical_training
(
    id SERIAL PRIMARY KEY,
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    training_name VARCHAR(255),
    level VARCHAR(255),
    year INT,
    role VARCHAR(255),
    result VARCHAR(255),
    score NUMERIC
);

-- Create discipline_records table
CREATE TABLE public.discipline_records
(
    record_id VARCHAR(255),
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    department VARCHAR(255),
    FOREIGN KEY (department) REFERENCES public.mission_profile (department),
    year INT,
    month INT,
    record_type VARCHAR(255),
    severity VARCHAR(255),
    reason TEXT,
    PRIMARY KEY (record_id)
);

-- Create mission_log table
CREATE TABLE public.mission_log
(
    id SERIAL PRIMARY KEY,
    mission_id VARCHAR(255),
    department VARCHAR(255),
    FOREIGN KEY (department) REFERENCES public.mission_profile (department),
    year INT,
    month INT,
    mission_date DATE,
    planned_duration_hours NUMERIC,
    status VARCHAR(255),
    cancellation_reason VARCHAR(255),
    dominant_weather VARCHAR(255),
    avg_temperature_c NUMERIC,
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    role_on_mission VARCHAR(255),
    shift_hours NUMERIC,
    hours_category VARCHAR(255)
);

-- Create flight_operations table
CREATE TABLE public.flight_operations
(
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    department VARCHAR(255),
    FOREIGN KEY (department) REFERENCES public.mission_profile (department),
    year INT,
    month INT,
    planned_missions INT,
    completed_missions INT,
    cancelled_missions INT,
    flight_hours_real NUMERIC,
    flight_hours_training NUMERIC,
    flight_hours_combat NUMERIC,
    flight_hours_test NUMERIC,
    flight_hours_simulator NUMERIC,
    avg_temperature_c NUMERIC,
    avg_wind_speed_kmh NUMERIC,
    dominant_weather VARCHAR(255),
    primary_cancellation_reason NUMERIC,
    PRIMARY KEY (person_id, year, month)
);

-- Create shooting_performance table
CREATE TABLE public.shooting_performance
(
    shot_id VARCHAR(255),
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    department VARCHAR(255),
    FOREIGN KEY (department) REFERENCES public.mission_profile (department),
    shot_date DATE,
    shot_sequence_number INT,
    is_first_shot BOOLEAN,
    shot_type VARCHAR(255),
    outcome VARCHAR(255),
    PRIMARY KEY (shot_id)
);

-- Create standardization_exams table
CREATE TABLE public.standardization_exams
(
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    department VARCHAR(255),
    FOREIGN KEY (department) REFERENCES public.mission_profile (department),
    exam_year INT,
    standardization_score NUMERIC,
    flight_clearance VARCHAR(255),
    retake_required BOOLEAN,
    retake_score NUMERIC,
    final_clearance_status VARCHAR(255),
    evaluator_id VARCHAR(255),
    FOREIGN KEY (evaluator_id) REFERENCES public.personal (person_id),
    PRIMARY KEY (person_id, exam_year)
);

-- Create fuel_consumption table
CREATE TABLE public.fuel_consumption
(
    department VARCHAR(255),
    FOREIGN KEY (department) REFERENCES public.mission_profile (department),
    year INT,
    total_flight_hours_real NUMERIC,
    total_flight_hours_simulator NUMERIC,
    primary_uav_model TEXT,
    avg_technical_condition_score NUMERIC,
    fuel_burn_rate_l_per_hour NUMERIC,
    total_fuel_liters NUMERIC,
    estimated_flying_days INT,
    PRIMARY KEY (department, year)
);

-- Create flight_safety table
CREATE TABLE public.flight_safety
(
    incident_id VARCHAR(255),
    mission_id VARCHAR(255),
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    department VARCHAR(255),
    FOREIGN KEY (department) REFERENCES public.mission_profile (department),
    incident_date DATE,
    incident_type VARCHAR(255),
    cause VARCHAR(255),
    severity_score INT,
    investigation_outcome VARCHAR(255),
    PRIMARY KEY (incident_id)
);

-- Create medals table
CREATE TABLE public.medals
(
    medal_id VARCHAR(255),
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    department VARCHAR(255),
    FOREIGN KEY (department) REFERENCES public.mission_profile (department),
    medal_type VARCHAR(255),
    award_date DATE,
    reason TEXT,
    PRIMARY KEY (medal_id)
);

-- Create risk_score table
CREATE TABLE public.risk_score
(
    person_id VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES public.personal (person_id),
    risk_score NUMERIC,
    risk_flight NUMERIC,
    risk_exam NUMERIC,
    risk_shoot NUMERIC,
    risk_disc_safety NUMERIC,
    risk_training NUMERIC,
    department VARCHAR(255),
    rank VARCHAR(255),
    specialization VARCHAR(255),
    PRIMARY KEY (person_id)
);

-- Create aircraft_monthly_maintenance table
CREATE TABLE public.aircraft_monthly_maintenance
(
    id SERIAL PRIMARY KEY,
    aircraft_id VARCHAR(255),
    FOREIGN KEY (aircraft_id) REFERENCES public.aircraft (aircraft_id),
    department VARCHAR(255),
    year INT,
    month INT,
    maintenance_hours NUMERIC,
    technician_id VARCHAR(255),
    FOREIGN KEY (technician_id) REFERENCES public.personal (person_id),
    effective_condition_score NUMERIC
);

-- Create mission_technical_log table
CREATE TABLE public.mission_technical_log
(
    mission_id VARCHAR(255),
    aircraft_id VARCHAR(255),
    FOREIGN KEY (aircraft_id) REFERENCES public.aircraft (aircraft_id),
    department VARCHAR(255),
    year INT,
    month INT,
    mission_date DATE,
    aircraft_age_years INT,
    planned_duration_hours NUMERIC,
    actual_duration_hours NUMERIC,
    hours_returned_early NUMERIC,
    pre_flight_check_minutes NUMERIC,
    pre_flight_issue_found BOOLEAN,
    post_flight_check_minutes NUMERIC,
    had_inflight_technical_problem BOOLEAN,
    problem_type VARCHAR(255),
    problem_duration_minutes NUMERIC,
    effective_condition_score NUMERIC,
    PRIMARY KEY (mission_id)
);

-- Indexes on foreign key columns for better join performance
CREATE INDEX idx_personal_department ON public.personal (department);
CREATE INDEX idx_aircraft_department ON public.aircraft (department);
CREATE INDEX idx_tactical_training_person_id ON public.tactical_training (person_id);
CREATE INDEX idx_discipline_records_person_id ON public.discipline_records (person_id);
CREATE INDEX idx_discipline_records_department ON public.discipline_records (department);
CREATE INDEX idx_mission_log_department ON public.mission_log (department);
CREATE INDEX idx_mission_log_person_id ON public.mission_log (person_id);
CREATE INDEX idx_flight_operations_department ON public.flight_operations (department);
CREATE INDEX idx_shooting_performance_person_id ON public.shooting_performance (person_id);
CREATE INDEX idx_shooting_performance_department ON public.shooting_performance (department);
CREATE INDEX idx_standardization_exams_department ON public.standardization_exams (department);
CREATE INDEX idx_standardization_exams_evaluator_id ON public.standardization_exams (evaluator_id);
CREATE INDEX idx_flight_safety_person_id ON public.flight_safety (person_id);
CREATE INDEX idx_flight_safety_department ON public.flight_safety (department);
CREATE INDEX idx_medals_person_id ON public.medals (person_id);
CREATE INDEX idx_medals_department ON public.medals (department);
CREATE INDEX idx_aircraft_monthly_maintenance_aircraft_id ON public.aircraft_monthly_maintenance (aircraft_id);
CREATE INDEX idx_aircraft_monthly_maintenance_technician_id ON public.aircraft_monthly_maintenance (technician_id);
CREATE INDEX idx_mission_technical_log_aircraft_id ON public.mission_technical_log (aircraft_id);