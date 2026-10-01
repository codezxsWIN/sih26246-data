PRAGMA foreign_keys=ON;
PRAGMA user_version=1;

CREATE TABLE source_files (
    source_file_id TEXT PRIMARY KEY,
    repository_path TEXT NOT NULL UNIQUE,
    sha256 TEXT NOT NULL CHECK(length(sha256)=64)
);
CREATE TABLE employers (
    employer_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    source_id TEXT NOT NULL,
    source_file_id TEXT NOT NULL REFERENCES source_files(source_file_id),
    UNIQUE(source_id, company_name)
);
CREATE TABLE recruiter_accounts (
    recruiter_id TEXT PRIMARY KEY,
    employer_id TEXT NOT NULL REFERENCES employers(employer_id),
    source_file_id TEXT NOT NULL REFERENCES source_files(source_file_id),
    permission_evidence_reference TEXT NOT NULL CHECK(length(trim(permission_evidence_reference))>0)
);
CREATE TABLE job_postings (
    posting_id TEXT PRIMARY KEY,
    employer_id TEXT NOT NULL REFERENCES employers(employer_id),
    source_id TEXT NOT NULL,
    source_job_id TEXT NOT NULL,
    job_title TEXT NOT NULL,
    occupation TEXT NOT NULL,
    location TEXT NOT NULL,
    job_url TEXT NOT NULL,
    posted_date TEXT,
    date_semantics TEXT NOT NULL,
    observed_date TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    status TEXT NOT NULL,
    vacancy_count INTEGER CHECK(vacancy_count IS NULL OR vacancy_count>=0),
    source_tier INTEGER NOT NULL CHECK(source_tier IN (1,2,3)),
    eligible_for_verified_market_demand INTEGER NOT NULL CHECK(eligible_for_verified_market_demand IN (0,1)),
    source_is_ncs INTEGER NOT NULL CHECK(source_is_ncs IN (0,1)),
    usage_permission TEXT NOT NULL,
    coverage TEXT NOT NULL,
    source_file_id TEXT NOT NULL REFERENCES source_files(source_file_id),
    UNIQUE(source_id, source_job_id, observed_at)
);
CREATE INDEX jobs_location_occupation ON job_postings(location, occupation, observed_date);
CREATE TABLE job_skills (
    posting_id TEXT NOT NULL REFERENCES job_postings(posting_id),
    skill_id TEXT NOT NULL,
    matched_text TEXT NOT NULL,
    evidence_scope TEXT NOT NULL,
    source_url TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    PRIMARY KEY(posting_id, skill_id)
);
CREATE INDEX job_skills_skill ON job_skills(skill_id);
CREATE TABLE aggregate_demand (
    observation_id INTEGER PRIMARY KEY,
    metric TEXT NOT NULL CHECK(metric IN ('Vacancies','Active Employer')),
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
