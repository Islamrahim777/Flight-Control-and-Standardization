-- Auto-generated MySQL schema for uav_analytics portfolio
-- Run: mysql -u youruser -p --local-infile=1 < mysql_schema.sql
CREATE DATABASE IF NOT EXISTS uav_analytics;
USE uav_analytics;
SET FOREIGN_KEY_CHECKS=0;  -- stays OFF through creates + loads; re-enabled at the very end

DROP TABLE IF EXISTS `personal`;
CREATE TABLE `personal` (
  `person_id` VARCHAR(100),
  `first_name` TEXT,
  `last_name` TEXT,
  `father_name` TEXT,
  `gender` VARCHAR(100),
  `fin_code` TEXT,
  `id_card_number` TEXT,
  `military_ticket_number` TEXT,
  `has_driving_license` TINYINT(1),
  `driving_license_number` TEXT,
  `birth_date` DATE,
  `age` INT,
  `home_region` VARCHAR(100),
  `education_level` VARCHAR(100),
  `university_admission_year` INT,
  `university_graduation_year` INT,
  `rank_group` VARCHAR(100),
  `rank` VARCHAR(100),
  `specialization` VARCHAR(100),
  `is_leadership` TINYINT(1),
  `officer_commissioning_source` VARCHAR(100),
  `military_academy_type` VARCHAR(100),
  `years_as_enlisted_before_commission` DOUBLE,
  `prior_enlisted_specialization` VARCHAR(100),
  `department` VARCHAR(100),
  `total_military_service_years` DOUBLE,
  `uav_service_years` DOUBLE,
  `current_department_years` DOUBLE,
  `rotation_count` INT,
  `last_rotation_date` DATE,
  `contract_start_date` DATE,
  `contract_end_date` DATE,
  `contract_length_years` INT,
  `pua_course_cohort` INT,
  PRIMARY KEY (`person_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `rank_history`;
CREATE TABLE `rank_history` (
  `person_id` VARCHAR(100),
  `current_rank` TEXT,
  `current_rank_date` DATE,
  `previous_rank` TEXT,
  `previous_rank_date` DATE,
  `current_rank_tenure_years` DOUBLE,
  `years_since_last_promotion` DOUBLE,
  PRIMARY KEY (`person_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `previous_service`;
CREATE TABLE `previous_service` (
  `person_id` VARCHAR(100),
  `previous_branch` VARCHAR(100),
  `years_in_previous_branch` DOUBLE,
  PRIMARY KEY (`person_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `rank_delay_analysis`;
CREATE TABLE `rank_delay_analysis` (
  `person_id` VARCHAR(100),
  `transferred_from_other_branch` TINYINT(1),
  `rank_delayed` TEXT,
  `delay_years` DOUBLE,
  `department` VARCHAR(100),
  `rank` VARCHAR(100),
  PRIMARY KEY (`person_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `certifications`;
CREATE TABLE `certifications` (
  `person_id` VARCHAR(100),
  `english_certified` TINYINT(1),
  `russian_certified` TINYINT(1),
  `other_language_certified` TINYINT(1),
  `other_language_name` VARCHAR(100),
  `nato_training` TINYINT(1),
  `foreign_course` TINYINT(1),
  `instructor_certified` TINYINT(1),
  PRIMARY KEY (`person_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `fitness_standards`;
CREATE TABLE `fitness_standards` (
  `age_group` INT,
  `age_range` VARCHAR(100),
  `score` INT,
  `pullups_required` INT,
  `run_minutes_required` DOUBLE,
  `is_passing` TINYINT(1),
  PRIMARY KEY (`age_group`, `score`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `physical_fitness`;
CREATE TABLE `physical_fitness` (
  `person_id` VARCHAR(100),
  `year` INT,
  `age_group` INT,
  `pullups_count` INT,
  `run_3km_minutes` DOUBLE,
  `pullup_score` DOUBLE,
  `run_score` DOUBLE,
  `fitness_score` DOUBLE,
  `result` VARCHAR(100),
  PRIMARY KEY (`person_id`, `year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `tactical_training`;
CREATE TABLE `tactical_training` (
  `person_id` VARCHAR(100),
  `training_name` VARCHAR(100),
  `level` VARCHAR(100),
  `year` INT,
  `role` VARCHAR(100),
  `result` VARCHAR(100),
  `score` DOUBLE,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `discipline_records`;
CREATE TABLE `discipline_records` (
  `record_id` INT AUTO_INCREMENT,
  `person_id` VARCHAR(100),
  `department` VARCHAR(100),
  `year` INT,
  `month` INT,
  `record_type` VARCHAR(100),
  `severity` VARCHAR(100),
  `reason` TEXT,
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `mission_log`;
CREATE TABLE `mission_log` (
  `mission_id` VARCHAR(100),
  `department` VARCHAR(100),
  `year` INT,
  `month` INT,
  `mission_date` DATE,
  `planned_duration_hours` DOUBLE,
  `status` VARCHAR(100),
  `cancellation_reason` VARCHAR(100),
  `dominant_weather` VARCHAR(100),
  `avg_temperature_c` DOUBLE,
  `person_id` VARCHAR(100),
  `role_on_mission` VARCHAR(100),
  `shift_hours` DOUBLE,
  `hours_category` VARCHAR(100),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `flight_operations`;
CREATE TABLE `flight_operations` (
  `person_id` VARCHAR(100),
  `department` VARCHAR(100),
  `year` INT,
  `month` INT,
  `planned_missions` INT,
  `completed_missions` INT,
  `cancelled_missions` INT,
  `flight_hours_real` DOUBLE,
  `flight_hours_training` DOUBLE,
  `flight_hours_combat` DOUBLE,
  `flight_hours_test` DOUBLE,
  `flight_hours_simulator` DOUBLE,
  `avg_temperature_c` DOUBLE,
  `avg_wind_speed_kmh` DOUBLE,
  `dominant_weather` VARCHAR(100),
  `primary_cancellation_reason` DOUBLE,
  PRIMARY KEY (`person_id`, `year`, `month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `shooting_performance`;
CREATE TABLE `shooting_performance` (
  `shot_id` VARCHAR(100),
  `person_id` VARCHAR(100),
  `department` VARCHAR(100),
  `shot_date` DATE,
  `shot_sequence_number` INT,
  `is_first_shot` TINYINT(1),
  `shot_type` VARCHAR(100),
  `outcome` VARCHAR(100),
  PRIMARY KEY (`shot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `standardization_exams`;
CREATE TABLE `standardization_exams` (
  `person_id` VARCHAR(100),
  `department` VARCHAR(100),
  `exam_year` INT,
  `standardization_score` DOUBLE,
  `flight_clearance` VARCHAR(100),
  `retake_required` TINYINT(1),
  `retake_score` DOUBLE,
  `final_clearance_status` VARCHAR(100),
  `evaluator_id` VARCHAR(100),
  PRIMARY KEY (`person_id`, `exam_year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `fuel_consumption`;
CREATE TABLE `fuel_consumption` (
  `department` VARCHAR(100),
  `year` INT,
  `total_flight_hours_real` DOUBLE,
  `total_flight_hours_simulator` DOUBLE,
  `primary_uav_model` TEXT,
  `avg_technical_condition_score` DOUBLE,
  `fuel_burn_rate_l_per_hour` DOUBLE,
  `total_fuel_liters` DOUBLE,
  `estimated_flying_days` INT,
  PRIMARY KEY (`department`, `year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `flight_safety`;
CREATE TABLE `flight_safety` (
  `incident_id` VARCHAR(100),
  `mission_id` VARCHAR(100),
  `person_id` VARCHAR(100),
  `department` VARCHAR(100),
  `incident_date` DATE,
  `incident_type` VARCHAR(100),
  `cause` VARCHAR(100),
  `severity_score` INT,
  `investigation_outcome` VARCHAR(100),
  PRIMARY KEY (`incident_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `medals`;
CREATE TABLE `medals` (
  `medal_id` VARCHAR(100),
  `person_id` VARCHAR(100),
  `department` VARCHAR(100),
  `medal_type` VARCHAR(100),
  `award_date` DATE,
  `reason` TEXT,
  PRIMARY KEY (`medal_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `mission_profile`;
CREATE TABLE `mission_profile` (
  `department` VARCHAR(100),
  `target_sector` VARCHAR(100),
  `climb_hours` DOUBLE,
  `transit_to_target_hours` DOUBLE,
  `transit_return_hours` DOUBLE,
  `descent_hours` DOUBLE,
  `max_flight_duration_hours` DOUBLE,
  `total_transit_hours` DOUBLE,
  `target_dwell_hours` DOUBLE,
  `mission_effectiveness_pct` DOUBLE,
  PRIMARY KEY (`department`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `risk_score`;
CREATE TABLE `risk_score` (
  `person_id` VARCHAR(100),
  `risk_score` DOUBLE,
  `risk_flight` DOUBLE,
  `risk_exam` DOUBLE,
  `risk_shoot` DOUBLE,
  `risk_disc_safety` DOUBLE,
  `risk_training` DOUBLE,
  `department` VARCHAR(100),
  `rank` VARCHAR(100),
  `specialization` VARCHAR(100),
  PRIMARY KEY (`person_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `aircraft`;
CREATE TABLE `aircraft` (
  `aircraft_id` VARCHAR(100),
  `department` VARCHAR(100),
  `model` VARCHAR(100),
  `in_service_date` DATE,
  `base_condition_score` DOUBLE,
  PRIMARY KEY (`aircraft_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `aircraft_monthly_maintenance`;
CREATE TABLE `aircraft_monthly_maintenance` (
  `aircraft_id` VARCHAR(100),
  `department` VARCHAR(100),
  `year` INT,
  `month` INT,
  `maintenance_hours` DOUBLE,
  `technician_id` VARCHAR(100),
  `effective_condition_score` DOUBLE,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `mission_technical_log`;
CREATE TABLE `mission_technical_log` (
  `mission_id` VARCHAR(100),
  `aircraft_id` VARCHAR(100),
  `department` VARCHAR(100),
  `year` INT,
  `month` INT,
  `mission_date` DATE,
  `aircraft_age_years` INT,
  `planned_duration_hours` DOUBLE,
  `actual_duration_hours` DOUBLE,
  `hours_returned_early` DOUBLE,
  `pre_flight_check_minutes` DOUBLE,
  `pre_flight_issue_found` TINYINT(1),
  `post_flight_check_minutes` DOUBLE,
  `had_inflight_technical_problem` TINYINT(1),
  `problem_type` VARCHAR(100),
  `problem_duration_minutes` DOUBLE,
  `effective_condition_score` DOUBLE,
  PRIMARY KEY (`mission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ FOREIGN KEYS (added after all tables exist) ============
ALTER TABLE `personal` ADD CONSTRAINT `fk_personal_department_0` FOREIGN KEY (`department`) REFERENCES `mission_profile`(`department`);
ALTER TABLE `rank_history` ADD CONSTRAINT `fk_rank_history_person_id_1` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `previous_service` ADD CONSTRAINT `fk_previous_service_person_id_2` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `rank_delay_analysis` ADD CONSTRAINT `fk_rank_delay_analysis_person_id_3` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `certifications` ADD CONSTRAINT `fk_certifications_person_id_4` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `physical_fitness` ADD CONSTRAINT `fk_physical_fitness_person_id_5` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `tactical_training` ADD CONSTRAINT `fk_tactical_training_person_id_6` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `discipline_records` ADD CONSTRAINT `fk_discipline_records_person_id_7` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `discipline_records` ADD CONSTRAINT `fk_discipline_records_department_8` FOREIGN KEY (`department`) REFERENCES `mission_profile`(`department`);
ALTER TABLE `mission_log` ADD CONSTRAINT `fk_mission_log_person_id_9` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `mission_log` ADD CONSTRAINT `fk_mission_log_department_10` FOREIGN KEY (`department`) REFERENCES `mission_profile`(`department`);
ALTER TABLE `flight_operations` ADD CONSTRAINT `fk_flight_operations_person_id_11` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `flight_operations` ADD CONSTRAINT `fk_flight_operations_department_12` FOREIGN KEY (`department`) REFERENCES `mission_profile`(`department`);
ALTER TABLE `shooting_performance` ADD CONSTRAINT `fk_shooting_performance_person_id_13` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `shooting_performance` ADD CONSTRAINT `fk_shooting_performance_department_14` FOREIGN KEY (`department`) REFERENCES `mission_profile`(`department`);
ALTER TABLE `standardization_exams` ADD CONSTRAINT `fk_standardization_exams_person_id_15` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `standardization_exams` ADD CONSTRAINT `fk_standardization_exams_department_16` FOREIGN KEY (`department`) REFERENCES `mission_profile`(`department`);
ALTER TABLE `fuel_consumption` ADD CONSTRAINT `fk_fuel_consumption_department_17` FOREIGN KEY (`department`) REFERENCES `mission_profile`(`department`);
ALTER TABLE `flight_safety` ADD CONSTRAINT `fk_flight_safety_person_id_18` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `flight_safety` ADD CONSTRAINT `fk_flight_safety_department_19` FOREIGN KEY (`department`) REFERENCES `mission_profile`(`department`);
ALTER TABLE `medals` ADD CONSTRAINT `fk_medals_person_id_20` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `medals` ADD CONSTRAINT `fk_medals_department_21` FOREIGN KEY (`department`) REFERENCES `mission_profile`(`department`);
ALTER TABLE `risk_score` ADD CONSTRAINT `fk_risk_score_person_id_22` FOREIGN KEY (`person_id`) REFERENCES `personal`(`person_id`);
ALTER TABLE `aircraft` ADD CONSTRAINT `fk_aircraft_department_23` FOREIGN KEY (`department`) REFERENCES `mission_profile`(`department`);
ALTER TABLE `aircraft_monthly_maintenance` ADD CONSTRAINT `fk_aircraft_monthly_maintenance_aircraft_id_24` FOREIGN KEY (`aircraft_id`) REFERENCES `aircraft`(`aircraft_id`);
ALTER TABLE `mission_technical_log` ADD CONSTRAINT `fk_mission_technical_log_aircraft_id_25` FOREIGN KEY (`aircraft_id`) REFERENCES `aircraft`(`aircraft_id`);

-- ============ LOAD DATA ============
-- IMPORTANT: MySQL's LOAD DATA INFILE needs a LITERAL file path (no variables).
-- Before running, find-and-replace /PATH/TO/data/ below with your real absolute
-- path to the project's data/ folder, e.g. /Users/yourname/Downloads/uav-analytics-portfolio/data/

LOAD DATA LOCAL INFILE '/PATH/TO/data/personal.csv'
INTO TABLE `personal`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`person_id`, `first_name`, `last_name`, `father_name`, `gender`, `fin_code`, `id_card_number`, `military_ticket_number`, @v_has_driving_license, `driving_license_number`, `birth_date`, `age`, `home_region`, `education_level`, `university_admission_year`, `university_graduation_year`, `rank_group`, `rank`, `specialization`, @v_is_leadership, `officer_commissioning_source`, `military_academy_type`, `years_as_enlisted_before_commission`, `prior_enlisted_specialization`, `department`, `total_military_service_years`, `uav_service_years`, `current_department_years`, `rotation_count`, `last_rotation_date`, `contract_start_date`, `contract_end_date`, `contract_length_years`, `pua_course_cohort`)
SET `has_driving_license` = CASE @v_has_driving_license WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END,
    `is_leadership` = CASE @v_is_leadership WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END;

LOAD DATA LOCAL INFILE '/PATH/TO/data/rank_history.csv'
INTO TABLE `rank_history`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`person_id`, `current_rank`, `current_rank_date`, `previous_rank`, `previous_rank_date`, `current_rank_tenure_years`, `years_since_last_promotion`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/previous_service.csv'
INTO TABLE `previous_service`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`person_id`, `previous_branch`, `years_in_previous_branch`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/rank_delay_analysis.csv'
INTO TABLE `rank_delay_analysis`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`person_id`, @v_transferred_from_other_branch, `rank_delayed`, `delay_years`, `department`, `rank`)
SET `transferred_from_other_branch` = CASE @v_transferred_from_other_branch WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END;

LOAD DATA LOCAL INFILE '/PATH/TO/data/certifications.csv'
INTO TABLE `certifications`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`person_id`, @v_english_certified, @v_russian_certified, @v_other_language_certified, `other_language_name`, @v_nato_training, @v_foreign_course, @v_instructor_certified)
SET `english_certified` = CASE @v_english_certified WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END,
    `russian_certified` = CASE @v_russian_certified WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END,
    `other_language_certified` = CASE @v_other_language_certified WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END,
    `nato_training` = CASE @v_nato_training WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END,
    `foreign_course` = CASE @v_foreign_course WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END,
    `instructor_certified` = CASE @v_instructor_certified WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END;

LOAD DATA LOCAL INFILE '/PATH/TO/data/fitness_standards.csv'
INTO TABLE `fitness_standards`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`age_group`, `age_range`, `score`, `pullups_required`, `run_minutes_required`, @v_is_passing)
SET `is_passing` = CASE @v_is_passing WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END;

LOAD DATA LOCAL INFILE '/PATH/TO/data/physical_fitness.csv'
INTO TABLE `physical_fitness`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`person_id`, `year`, `age_group`, `pullups_count`, `run_3km_minutes`, `pullup_score`, `run_score`, `fitness_score`, `result`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/tactical_training.csv'
INTO TABLE `tactical_training`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`person_id`, `training_name`, `level`, `year`, `role`, `result`, `score`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/discipline_records.csv'
INTO TABLE `discipline_records`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`record_id`, `person_id`, `department`, `year`, `month`, `record_type`, `severity`, `reason`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/mission_log.csv'
INTO TABLE `mission_log`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`mission_id`, `department`, `year`, `month`, `mission_date`, `planned_duration_hours`, `status`, `cancellation_reason`, `dominant_weather`, `avg_temperature_c`, `person_id`, `role_on_mission`, `shift_hours`, `hours_category`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/flight_operations.csv'
INTO TABLE `flight_operations`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`person_id`, `department`, `year`, `month`, `planned_missions`, `completed_missions`, `cancelled_missions`, `flight_hours_real`, `flight_hours_training`, `flight_hours_combat`, `flight_hours_test`, `flight_hours_simulator`, `avg_temperature_c`, `avg_wind_speed_kmh`, `dominant_weather`, `primary_cancellation_reason`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/shooting_performance.csv'
INTO TABLE `shooting_performance`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`shot_id`, `person_id`, `department`, `shot_date`, `shot_sequence_number`, @v_is_first_shot, `shot_type`, `outcome`)
SET `is_first_shot` = CASE @v_is_first_shot WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END;

LOAD DATA LOCAL INFILE '/PATH/TO/data/standardization_exams.csv'
INTO TABLE `standardization_exams`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`person_id`, `department`, `exam_year`, `standardization_score`, `flight_clearance`, @v_retake_required, `retake_score`, `final_clearance_status`, `evaluator_id`)
SET `retake_required` = CASE @v_retake_required WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END;

LOAD DATA LOCAL INFILE '/PATH/TO/data/fuel_consumption.csv'
INTO TABLE `fuel_consumption`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`department`, `year`, `total_flight_hours_real`, `total_flight_hours_simulator`, `primary_uav_model`, `avg_technical_condition_score`, `fuel_burn_rate_l_per_hour`, `total_fuel_liters`, `estimated_flying_days`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/flight_safety.csv'
INTO TABLE `flight_safety`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`incident_id`, `mission_id`, `person_id`, `department`, `incident_date`, `incident_type`, `cause`, `severity_score`, `investigation_outcome`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/medals.csv'
INTO TABLE `medals`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`medal_id`, `person_id`, `department`, `medal_type`, `award_date`, `reason`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/mission_profile.csv'
INTO TABLE `mission_profile`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`department`, `target_sector`, `climb_hours`, `transit_to_target_hours`, `transit_return_hours`, `descent_hours`, `max_flight_duration_hours`, `total_transit_hours`, `target_dwell_hours`, `mission_effectiveness_pct`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/risk_score.csv'
INTO TABLE `risk_score`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`person_id`, `risk_score`, `risk_flight`, `risk_exam`, `risk_shoot`, `risk_disc_safety`, `risk_training`, `department`, `rank`, `specialization`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/aircraft.csv'
INTO TABLE `aircraft`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`aircraft_id`, `department`, `model`, `in_service_date`, `base_condition_score`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/aircraft_monthly_maintenance.csv'
INTO TABLE `aircraft_monthly_maintenance`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`aircraft_id`, `department`, `year`, `month`, `maintenance_hours`, `technician_id`, `effective_condition_score`);

LOAD DATA LOCAL INFILE '/PATH/TO/data/mission_technical_log.csv'
INTO TABLE `mission_technical_log`
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`mission_id`, `aircraft_id`, `department`, `year`, `month`, `mission_date`, `aircraft_age_years`, `planned_duration_hours`, `actual_duration_hours`, `hours_returned_early`, `pre_flight_check_minutes`, @v_pre_flight_issue_found, `post_flight_check_minutes`, @v_had_inflight_technical_problem, `problem_type`, `problem_duration_minutes`, `effective_condition_score`)
SET `pre_flight_issue_found` = CASE @v_pre_flight_issue_found WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END,
    `had_inflight_technical_problem` = CASE @v_had_inflight_technical_problem WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END;

SET FOREIGN_KEY_CHECKS=1;
SELECT 'Import complete.' AS status;
