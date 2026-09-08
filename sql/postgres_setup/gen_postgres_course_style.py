import pandas as pd

DATE_COLS = {'birth_date','last_rotation_date','contract_start_date','contract_end_date',
             'current_rank_date','previous_rank_date','mission_date','shot_date',
             'award_date','in_service_date','incident_date'}

PK = {
 'personal':['person_id'],'rank_history':['person_id'],'previous_service':['person_id'],
 'rank_delay_analysis':['person_id'],'certifications':['person_id'],
 'shooting_performance':['shot_id'],'mission_profile':['department'],
 'flight_safety':['incident_id'],'medals':['medal_id'],'risk_score':['person_id'],
 'aircraft':['aircraft_id'],'mission_technical_log':['mission_id'],
 'discipline_records':['record_id'],
 'physical_fitness':['person_id','year'],
 'flight_operations':['person_id','year','month'],
 'standardization_exams':['person_id','exam_year'],
 'fuel_consumption':['department','year'],
 'fitness_standards':['age_group','score'],
}
NEEDS_SYNTHETIC_ID = {'tactical_training', 'mission_log', 'aircraft_monthly_maintenance'}

# Dependency order: referenced tables first
ORDER = ['mission_profile','personal','aircraft','rank_history','previous_service',
         'rank_delay_analysis','certifications','fitness_standards','physical_fitness',
         'tactical_training','discipline_records','mission_log','flight_operations',
         'shooting_performance','standardization_exams','fuel_consumption','flight_safety',
         'medals','risk_score','aircraft_monthly_maintenance','mission_technical_log']

# (table, column) -> (ref_table, ref_column)
FK_MAP = {
    ('personal','department'):('mission_profile','department'),
    ('aircraft','department'):('mission_profile','department'),
    ('rank_history','person_id'):('personal','person_id'),
    ('previous_service','person_id'):('personal','person_id'),
    ('rank_delay_analysis','person_id'):('personal','person_id'),
    ('certifications','person_id'):('personal','person_id'),
    ('physical_fitness','person_id'):('personal','person_id'),
    ('tactical_training','person_id'):('personal','person_id'),
    ('discipline_records','person_id'):('personal','person_id'),
    ('discipline_records','department'):('mission_profile','department'),
    ('mission_log','person_id'):('personal','person_id'),
    ('mission_log','department'):('mission_profile','department'),
    ('flight_operations','person_id'):('personal','person_id'),
    ('flight_operations','department'):('mission_profile','department'),
    ('shooting_performance','person_id'):('personal','person_id'),
    ('shooting_performance','department'):('mission_profile','department'),
    ('standardization_exams','person_id'):('personal','person_id'),
    ('standardization_exams','evaluator_id'):('personal','person_id'),
    ('standardization_exams','department'):('mission_profile','department'),
    ('fuel_consumption','department'):('mission_profile','department'),
    ('flight_safety','person_id'):('personal','person_id'),
    ('flight_safety','department'):('mission_profile','department'),
    # NOTE: flight_safety.mission_id conceptually links to mission_log.mission_id,
    # but mission_id is NOT unique in mission_log (repeats once per crew member),
    # so it cannot be a valid FK target — left as a plain column, joinable but unenforced.
    ('medals','person_id'):('personal','person_id'),
    ('medals','department'):('mission_profile','department'),
    ('risk_score','person_id'):('personal','person_id'),
    ('aircraft_monthly_maintenance','aircraft_id'):('aircraft','aircraft_id'),
    ('aircraft_monthly_maintenance','technician_id'):('personal','person_id'),
    ('mission_technical_log','aircraft_id'):('aircraft','aircraft_id'),
    # NOTE: mission_technical_log.mission_id also conceptually links to mission_log,
    # same non-unique-target issue as above — left unenforced, still joinable.
}

def sql_type(col, dtype):
    if col in DATE_COLS:
        return 'DATE'
    if dtype == 'bool':
        return 'BOOLEAN'
    if dtype == 'int64':
        return 'INT'
    if dtype == 'float64':
        return 'NUMERIC'
    if col.endswith('_id') or col in ('rank','department','gender','result','status',
        'record_type','severity','incident_type','role','level','shot_type','outcome',
        'rank_group','specialization','education_level','home_region','model',
        'flight_clearance','final_clearance_status','age_range','dominant_weather',
        'hours_category','role_on_mission','medal_type','cause','investigation_outcome',
        'previous_branch','other_language_name','prior_enlisted_specialization',
        'officer_commissioning_source','military_academy_type','target_sector',
        'training_name','cancellation_reason','problem_type','primary_cancellation_reason'):
        return 'VARCHAR(255)'
    return 'TEXT'

# ============ File 1: create database ============
with open('1_create_database.sql', 'w') as f:
    f.write("CREATE DATABASE uav_analytics;\n\n-- DROP DATABASE IF EXISTS uav_analytics;\n")

# ============ File 2: create tables (inline FKs + indexes, course style) ============
out2 = []
index_stmts = []
for t in ORDER:
    df = pd.read_csv(t + '.csv', nrows=200)
    cols = list(df.columns)
    dtypes = dict(df.dtypes.astype(str))

    out2.append(f"-- Create {t} table")
    out2.append(f"CREATE TABLE public.{t}")
    out2.append("(")
    coldefs = []
    if t in NEEDS_SYNTHETIC_ID:
        coldefs.append("    id SERIAL PRIMARY KEY")
    for c in cols:
        line = f"    {c} {sql_type(c, dtypes[c])}"
        fk = FK_MAP.get((t, c))
        if fk:
            line += f",\n    FOREIGN KEY ({c}) REFERENCES public.{fk[0]} ({fk[1]})"
        coldefs.append(line)
    if t not in NEEDS_SYNTHETIC_ID and PK.get(t):
        keycols = ", ".join(PK[t])
        coldefs.append(f"    PRIMARY KEY ({keycols})")
    out2.append(",\n".join(coldefs))
    out2.append(");\n")

    for c in cols:
        if (t, c) in FK_MAP and c != PK.get(t, [None])[0]:
            index_stmts.append(f"CREATE INDEX idx_{t}_{c} ON public.{t} ({c});")

out2.append("-- Indexes on foreign key columns for better join performance")
out2.extend(index_stmts)

with open('2_create_tables.sql', 'w') as f:
    f.write("\n".join(out2))

# ============ File 3: load data ============
out3 = []
out3.append("""/* ==========================================================================
Database Load Issues (follow if receiving permission denied when running the
COPY commands below)

If you get: 'could not open file "[path]/personal.csv" for reading: Permission denied.'

1. Open pgAdmin
2. In Object Explorer (left-hand pane), navigate to the uav_analytics database
3. Right-click uav_analytics and select 'PSQL Tool' (opens a terminal)
4. Get the absolute file path of your data/ folder
    - In VS Code, right-click a CSV file and select 'Copy Path'
5. Paste the \\copy commands below into the PSQL Tool, with YOUR correct path,
   e.g.:

\\copy mission_profile FROM '[Insert Path]/data/mission_profile.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

========================================================================== */

-- If running this whole file directly with `psql -f 3_load_data.sql`, edit the
-- path below first (find-and-replace [Insert Path] with your real absolute path).
""")

for t in ORDER:
    df = pd.read_csv(t + '.csv', nrows=200)
    cols = list(df.columns)
    col_list = ", ".join(cols)
    out3.append(f"\\copy {t}({col_list}) FROM '[Insert Path]/data/{t}.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');\n")

with open('3_load_data.sql', 'w') as f:
    f.write("\n".join(out3))

print("All 3 files written.")
