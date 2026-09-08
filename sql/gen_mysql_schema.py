import pandas as pd

TABLES = ['personal','rank_history','previous_service','rank_delay_analysis','certifications',
'fitness_standards','physical_fitness','tactical_training','discipline_records',
'mission_log','flight_operations','shooting_performance','standardization_exams',
'fuel_consumption','flight_safety','medals','mission_profile','risk_score',
'aircraft','aircraft_monthly_maintenance','mission_technical_log']

DATE_COLS = {'birth_date','last_rotation_date','contract_start_date','contract_end_date',
             'current_rank_date','previous_rank_date','mission_date','shot_date',
             'award_date','in_service_date','incident_date'}

PK = {
 'personal':'person_id','rank_history':'person_id','previous_service':'person_id',
 'rank_delay_analysis':'person_id','certifications':'person_id',
 'shooting_performance':'shot_id','fuel_consumption':None,'mission_profile':'department',
 'flight_safety':'incident_id','medals':'medal_id','risk_score':'person_id',
 'aircraft':'aircraft_id','mission_technical_log':'mission_id',
}
COMPOSITE_PK = {
 'physical_fitness':['person_id','year'],
 'flight_operations':['person_id','year','month'],
 'standardization_exams':['person_id','exam_year'],
 'fuel_consumption':['department','year'],
 'fitness_standards':['age_group','score'],
}
AUTOINC = {'discipline_records':'record_id','tactical_training':'id','mission_log':'id',
           'aircraft_monthly_maintenance':'id','mission_technical_log':'mission_id'}
# mission_technical_log's mission_id is already unique text PK actually, fix below

def sql_type(col, dtype):
    if col in DATE_COLS:
        return 'DATE'
    if dtype == 'bool':
        return 'TINYINT(1)'
    if dtype == 'int64':
        return 'INT'
    if dtype == 'float64':
        return 'DOUBLE'
    if col.endswith('_id') or col in ('rank','department','gender','result','status',
        'record_type','severity','incident_type','role','level','shot_type','outcome',
        'rank_group','specialization','education_level','home_region','model',
        'flight_clearance','final_clearance_status','age_range','dominant_weather',
        'hours_category','role_on_mission','medal_type','cause','investigation_outcome',
        'previous_branch','other_language_name','prior_enlisted_specialization',
        'officer_commissioning_source','military_academy_type','target_sector',
        'training_name','cancellation_reason','problem_type','primary_cancellation_reason'):
        return 'VARCHAR(100)'
    return 'TEXT'  # reason, notes, free text

out = []
out.append("-- Auto-generated MySQL schema for uav_analytics portfolio")
out.append("-- Run: mysql -u youruser -p --local-infile=1 < mysql_schema.sql")
out.append("CREATE DATABASE IF NOT EXISTS uav_analytics;")
out.append("USE uav_analytics;")
out.append("SET FOREIGN_KEY_CHECKS=0;  -- stays OFF through creates + loads; re-enabled at the very end\n")

FOREIGN_KEYS = [
    ('personal','department','mission_profile','department'),
    ('rank_history','person_id','personal','person_id'),
    ('previous_service','person_id','personal','person_id'),
    ('rank_delay_analysis','person_id','personal','person_id'),
    ('certifications','person_id','personal','person_id'),
    ('physical_fitness','person_id','personal','person_id'),
    ('tactical_training','person_id','personal','person_id'),
    ('discipline_records','person_id','personal','person_id'),
    ('discipline_records','department','mission_profile','department'),
    ('mission_log','person_id','personal','person_id'),
    ('mission_log','department','mission_profile','department'),
    ('flight_operations','person_id','personal','person_id'),
    ('flight_operations','department','mission_profile','department'),
    ('shooting_performance','person_id','personal','person_id'),
    ('shooting_performance','department','mission_profile','department'),
    ('standardization_exams','person_id','personal','person_id'),
    ('standardization_exams','department','mission_profile','department'),
    ('fuel_consumption','department','mission_profile','department'),
    ('flight_safety','person_id','personal','person_id'),
    ('flight_safety','department','mission_profile','department'),
    ('medals','person_id','personal','person_id'),
    ('medals','department','mission_profile','department'),
    ('risk_score','person_id','personal','person_id'),
    ('aircraft','department','mission_profile','department'),
    ('aircraft_monthly_maintenance','aircraft_id','aircraft','aircraft_id'),
    ('mission_technical_log','aircraft_id','aircraft','aircraft_id'),
]

bool_cols_by_table = {}

for t in TABLES:
    df = pd.read_csv(t+'.csv', nrows=200)
    cols = list(df.columns)
    dtypes = dict(df.dtypes.astype(str))
    bool_cols = [c for c,d in dtypes.items() if d=='bool']
    bool_cols_by_table[t] = bool_cols

    lines = [f"DROP TABLE IF EXISTS `{t}`;", f"CREATE TABLE `{t}` ("]
    coldefs = []
    for c in cols:
        coldefs.append(f"  `{c}` {sql_type(c, dtypes[c])}")
    # primary key
    if t in AUTOINC and t != 'mission_technical_log':
        idcol = AUTOINC[t]
        for i,cd in enumerate(coldefs):
            if cd.strip().startswith(f"`{idcol}`"):
                coldefs[i] = f"  `{idcol}` INT AUTO_INCREMENT"
        coldefs.append(f"  PRIMARY KEY (`{idcol}`)")
    elif t in COMPOSITE_PK:
        keycols = ", ".join(f"`{k}`" for k in COMPOSITE_PK[t])
        coldefs.append(f"  PRIMARY KEY ({keycols})")
    elif PK.get(t):
        coldefs.append(f"  PRIMARY KEY (`{PK[t]}`)")
    lines.append(",\n".join(coldefs))
    lines.append(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n")
    out.append("\n".join(lines))

out.append("-- ============ FOREIGN KEYS (added after all tables exist) ============")
for i, (tbl, col, ref_tbl, ref_col) in enumerate(FOREIGN_KEYS):
    out.append(f"ALTER TABLE `{tbl}` ADD CONSTRAINT `fk_{tbl}_{col}_{i}` "
                f"FOREIGN KEY (`{col}`) REFERENCES `{ref_tbl}`(`{ref_col}`);")
out.append("")

out.append("-- ============ LOAD DATA ============")
out.append("-- IMPORTANT: MySQL's LOAD DATA INFILE needs a LITERAL file path (no variables).")
out.append("-- Before running, find-and-replace /PATH/TO/data/ below with your real absolute")
out.append("-- path to the project's data/ folder, e.g. /Users/yourname/Downloads/uav-analytics-portfolio/data/\n")

for t in TABLES:
    df = pd.read_csv(t+'.csv', nrows=200)
    cols = list(df.columns)
    bool_cols = bool_cols_by_table[t]
    col_list = []
    for c in cols:
        col_list.append(f"@v_{c}" if c in bool_cols else f"`{c}`")
    set_clauses = [f"`{c}` = NULLIF(@v_{c},'')  = 'True'" for c in bool_cols]
    # Better: convert True/'' -> 1/0/NULL properly
    set_clauses = [f"`{c}` = CASE @v_{c} WHEN 'True' THEN 1 WHEN 'False' THEN 0 ELSE NULL END" for c in bool_cols]

    stmt = [f"LOAD DATA LOCAL INFILE '/PATH/TO/data/{t}.csv'",
            f"INTO TABLE `{t}`",
            "FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"'",
            "LINES TERMINATED BY '\\n'",
            "IGNORE 1 ROWS",
            f"({', '.join(col_list)})"]
    if set_clauses:
        stmt.append("SET " + ",\n    ".join(set_clauses))
    out.append("\n".join(stmt) + ";\n")

with open('/home/claude/mysql_schema.sql','w') as f:
    f.write("\n".join(out))
    f.write("\nSET FOREIGN_KEY_CHECKS=1;\n")
    f.write("SELECT 'Import complete.' AS status;\n")

print("Written. Lines:", len("\n".join(out).splitlines()))
