PRAGMA foreign_keys=ON;
PRAGMA user_version=1;

CREATE TABLE source_files (
    source_file_id TEXT PRIMARY KEY,
    repository_path TEXT NOT NULL UNIQUE,
    sha256 TEXT NOT NULL CHECK(length(sha256)=64)
);
CREATE TABLE candidate_profiles (
    candidate_id TEXT PRIMARY KEY CHECK(length(trim(candidate_id))>0),
    geography TEXT NOT NULL CHECK(length(trim(geography))>0),
    geography_level TEXT NOT NULL CHECK(geography_level IN ('city','district','state')),
    occupation TEXT NOT NULL CHECK(length(trim(occupation))>0),
    availability_status TEXT NOT NULL CHECK(availability_status IN ('available','unavailable','unknown')),
    availability_observed_at TEXT,
    source_file_id TEXT NOT NULL REFERENCES source_files(source_file_id),
    permission_scope TEXT NOT NULL CHECK(permission_scope='labour_market_analysis'),
    permission_evidence_reference TEXT NOT NULL CHECK(length(trim(permission_evidence_reference))>0),
    CHECK(availability_status='unknown' OR availability_observed_at IS NOT NULL)
);
CREATE INDEX candidates_geography_occupation ON candidate_profiles(geography, occupation, availability_status);
CREATE TABLE candidate_skills (
    candidate_id TEXT NOT NULL REFERENCES candidate_profiles(candidate_id),
    skill_id TEXT NOT NULL CHECK(length(trim(skill_id))>0),
    evidence_type TEXT NOT NULL CHECK(evidence_type IN ('self_reported','certified','assessed')),
    observed_at TEXT NOT NULL,
    source_file_id TEXT NOT NULL REFERENCES source_files(source_file_id),
    PRIMARY KEY(candidate_id, skill_id, evidence_type)
);
CREATE INDEX candidate_skills_skill ON candidate_skills(skill_id);
CREATE TABLE aggregate_jobseekers (
    observation_id INTEGER PRIMARY KEY,
    metric TEXT NOT NULL CHECK(metric IN ('Jobseeker Registered','Active Jobseekers')),
    state TEXT NOT NULL,
    financial_year TEXT NOT NULL,
    value INTEGER NOT NULL CHECK(value>=0),
    publisher_updated_at TEXT NOT NULL,
    source_url TEXT NOT NULL,
    access_method TEXT NOT NULL,
    quality_flag TEXT NOT NULL,
    source_file_id TEXT NOT NULL REFERENCES source_files(source_file_id),
    UNIQUE(metric, state, financial_year, publisher_updated_at)
);
CREATE TABLE labour_rates (
    observation_id INTEGER PRIMARY KEY,
    source_id TEXT NOT NULL,
    geography TEXT NOT NULL,
    geography_level TEXT NOT NULL,
    year TEXT NOT NULL,
    year_type TEXT,
    frequency TEXT NOT NULL,
    quarter TEXT,
    month TEXT,
    indicator TEXT NOT NULL,
    value REAL NOT NULL CHECK(value BETWEEN 0 AND 100),
    unit TEXT NOT NULL CHECK(unit='percent'),
    sector TEXT NOT NULL,
    gender TEXT NOT NULL,
    age_group TEXT NOT NULL,
    reference_status TEXT,
    education TEXT,
    religion TEXT,
    social_group TEXT,
    role_scope TEXT NOT NULL CHECK(role_scope='all_roles'),
    "use" TEXT NOT NULL CHECK("use"='workforce_baseline_only'),
    available_analyst_supply INTEGER NOT NULL CHECK(available_analyst_supply=0),
    methodology_note TEXT NOT NULL,
    evidence_file TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_file_id TEXT NOT NULL REFERENCES source_files(source_file_id)
);
CREATE INDEX rates_geography_period ON labour_rates(geography, year_type, frequency, year, quarter, month);
CREATE TABLE workforce_baselines (
    observation_id INTEGER PRIMARY KEY,
    geography TEXT NOT NULL,
    year TEXT NOT NULL,
    year_type TEXT,
    frequency TEXT NOT NULL,
    quarter TEXT,
    month TEXT,
    sector TEXT NOT NULL,
    gender TEXT NOT NULL,
    age_group TEXT NOT NULL,
    reference_status TEXT,
    education TEXT,
    religion TEXT,
    social_group TEXT,
    lfpr_percent REAL NOT NULL CHECK(lfpr_percent BETWEEN 0 AND 100),
    ur_percent REAL NOT NULL CHECK(ur_percent BETWEEN 0 AND 100),
    wpr_percent REAL NOT NULL CHECK(wpr_percent BETWEEN 0 AND 100),
    unemployed_per_100_population REAL NOT NULL CHECK(unemployed_per_100_population BETWEEN 0 AND 100),
    implied_employed_per_100_population REAL NOT NULL CHECK(implied_employed_per_100_population BETWEEN 0 AND 100),
    wpr_rounding_residual REAL NOT NULL,
    unit TEXT NOT NULL CHECK(unit='persons_per_100_population_in_matching_age_group'),
    available_data_analysts_estimate REAL CHECK(available_data_analysts_estimate IS NULL),
    role_scope TEXT NOT NULL CHECK(role_scope='all_roles'),
    "use" TEXT NOT NULL CHECK("use"='baseline_not_skill_supply'),
    formula TEXT NOT NULL,
    limitations TEXT NOT NULL,
    evidence_files TEXT NOT NULL,
    source_file_id TEXT NOT NULL REFERENCES source_files(source_file_id)
);
CREATE INDEX baselines_geography_period ON workforce_baselines(geography, year_type, frequency, year, quarter, month);
