"""Build public-safe recruiter and job-seeker SQLite snapshots."""
from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = {
    "employers": ROOT / "data/processed/live_employers/employer-snapshot-20261001-v1/public_employer_posting_observations.csv",
    "skills": ROOT / "data/processed/live_employers/employer-snapshot-20261001-v1/skill_mentions.csv",
    "ncs": ROOT / "data/processed/ncs/ncs_maharashtra_year_metrics.csv",
    "rates": ROOT / "data/processed/public_labour/public-labour-20261001-v2/plfs_workforce_rates.csv",
    "baselines": ROOT / "data/processed/public_labour/public-labour-20261001-v2/workforce_baseline_estimates.csv",
}

RECRUITER_SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE employers (employer_id TEXT PRIMARY KEY, company TEXT NOT NULL, evidence_url TEXT NOT NULL, source_tier INTEGER NOT NULL, usage_permission TEXT NOT NULL);
CREATE TABLE recruiter_accounts (recruiter_id TEXT PRIMARY KEY, employer_id TEXT, account_status TEXT NOT NULL CHECK(account_status IN ('unavailable','available')), FOREIGN KEY(employer_id) REFERENCES employers(employer_id));
CREATE TABLE job_postings (job_id TEXT PRIMARY KEY, employer_id TEXT NOT NULL, title TEXT NOT NULL, location TEXT NOT NULL, job_url TEXT NOT NULL, posted_date TEXT, observed_date TEXT NOT NULL, status TEXT NOT NULL, vacancy_count INTEGER, eligible_for_verified_market_demand INTEGER NOT NULL CHECK(eligible_for_verified_market_demand IN (0,1)), source_is_ncs INTEGER NOT NULL CHECK(source_is_ncs IN (0,1)), quality_flag TEXT NOT NULL, FOREIGN KEY(employer_id) REFERENCES employers(employer_id));
CREATE TABLE job_skills (job_id TEXT NOT NULL, skill_id TEXT NOT NULL, matched_text TEXT NOT NULL, evidence_scope TEXT NOT NULL, source_url TEXT NOT NULL, observed_at TEXT NOT NULL, PRIMARY KEY(job_id, skill_id), FOREIGN KEY(job_id) REFERENCES job_postings(job_id));
CREATE TABLE aggregate_demand (metric TEXT NOT NULL, geography TEXT NOT NULL, period TEXT NOT NULL, value INTEGER NOT NULL, source_url TEXT NOT NULL, quality_flag TEXT NOT NULL, PRIMARY KEY(metric, geography, period));
CREATE INDEX idx_job_postings_location ON job_postings(location);
CREATE INDEX idx_job_skills_skill ON job_skills(skill_id);
"""

JOBSEEKER_SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE candidate_profiles (candidate_id TEXT PRIMARY KEY, geography TEXT, profile_status TEXT NOT NULL CHECK(profile_status IN ('unavailable','consented','restricted')), consent_reference TEXT, created_at TEXT);
CREATE TABLE candidate_skills (candidate_id TEXT NOT NULL, skill_id TEXT NOT NULL, evidence_type TEXT NOT NULL, proficiency TEXT, PRIMARY KEY(candidate_id, skill_id), FOREIGN KEY(candidate_id) REFERENCES candidate_profiles(candidate_id));
CREATE TABLE aggregate_jobseekers (metric TEXT NOT NULL, geography TEXT NOT NULL, period TEXT NOT NULL, value INTEGER NOT NULL, source_url TEXT NOT NULL, quality_flag TEXT NOT NULL, PRIMARY KEY(metric, geography, period));
CREATE TABLE labour_rates (source_id TEXT NOT NULL, geography TEXT NOT NULL, year TEXT NOT NULL, year_type TEXT, frequency TEXT, quarter TEXT, month TEXT, indicator TEXT NOT NULL, value REAL NOT NULL, unit TEXT NOT NULL, reference_status TEXT, role_scope TEXT NOT NULL, use TEXT NOT NULL, source_url TEXT NOT NULL, PRIMARY KEY(source_id, geography, year, year_type, frequency, quarter, month, indicator));
CREATE TABLE workforce_baselines (geography TEXT NOT NULL, year TEXT NOT NULL, year_type TEXT, frequency TEXT, quarter TEXT, month TEXT, reference_status TEXT, lfpr_percent REAL, ur_percent REAL, wpr_percent REAL, implied_employed_per_100_population REAL, available_data_analysts_estimate REAL, role_scope TEXT NOT NULL, use TEXT NOT NULL, limitations TEXT NOT NULL, PRIMARY KEY(geography, year, year_type, frequency, quarter, month));
CREATE INDEX idx_aggregate_jobseekers_metric ON aggregate_jobseekers(metric, period);
CREATE INDEX idx_labour_rates_indicator ON labour_rates(indicator, year);
"""

def rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        yield from csv.DictReader(f)

def text(value):
    return value or None

def flag(value):
    return 1 if str(value).strip().lower() in ("1", "true", "yes") else 0

def insert_csv(con, folder: Path, table: str, fieldnames, records):
    folder.mkdir(parents=True, exist_ok=True)
    records = list(records)
    with (folder / f"{table}.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader(); writer.writerows(records)
    placeholders = ",".join("?" for _ in fieldnames)
    con.executemany(f"INSERT INTO {table} ({','.join(fieldnames)}) VALUES ({placeholders})", [[r.get(k) for k in fieldnames] for r in records])
    return len(records)

def build(output: Path | str = ROOT / "DATABASES"):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for name in ("recruiter.sqlite", "job_seekers.sqlite", "manifest.json"):
        if (output / name).exists(): raise FileExistsError(f"refusing to overwrite {output / name}")
    missing = [str(p) for p in SOURCE_FILES.values() if not p.exists()]
    if missing: raise FileNotFoundError("missing committed source files: " + ", ".join(missing))
    source_hashes = [{"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in SOURCE_FILES.values()]
    counts = {}
    db_specs = [("recruiter.sqlite", RECRUITER_SCHEMA, "recruiter_data"), ("job_seekers.sqlite", JOBSEEKER_SCHEMA, "job_seeker_data")]
    for name, schema, folder_name in db_specs:
        db = output / name; folder = output / folder_name
        con = sqlite3.connect(db); con.executescript(schema); con.execute("PRAGMA user_version=1")
        if name == "recruiter.sqlite":
            jobs = list(rows(SOURCE_FILES["employers"])); skills = list(rows(SOURCE_FILES["skills"])); ncs = list(rows(SOURCE_FILES["ncs"]))
            employers = [{"employer_id": r["source_id"], "company": r["company"], "evidence_url": r["job_url"], "source_tier": r["source_tier"], "usage_permission": r["usage_permission"]} for r in jobs]
            postings = [{"job_id": r["source_job_id"], "employer_id": r["source_id"], "title": r["job_title"], "location": r["location"], "job_url": r["job_url"], "posted_date": text(r["posted_date"]), "observed_date": r["observed_date"], "status": r["status"], "vacancy_count": text(r["vacancy_count"]), "eligible_for_verified_market_demand": flag(r["eligible_for_verified_market_demand"]), "source_is_ncs": flag(r["source_is_ncs"]), "quality_flag": r["coverage"]} for r in jobs]
            sk = [{"job_id": r["source_job_id"], "skill_id": r["skill_id"], "matched_text": r["matched_text"], "evidence_scope": r["evidence_scope"], "source_url": r["source_url"], "observed_at": r["observed_at"]} for r in skills]
            agg = [{"metric": r["metric"], "geography": r["state"], "period": r["financial_year"], "value": r["value"], "source_url": r["source_url"], "quality_flag": r["quality_flag"]} for r in ncs if r["metric"] in ("Vacancies", "Active Employer")]
            counts[name] = {"employers": insert_csv(con, folder, "employers", list(employers[0]), employers), "job_postings": insert_csv(con, folder, "job_postings", list(postings[0]), postings), "job_skills": insert_csv(con, folder, "job_skills", list(sk[0]), sk), "aggregate_demand": insert_csv(con, folder, "aggregate_demand", list(agg[0]), agg)}
            con.executemany("INSERT INTO metadata VALUES (?,?)", [("scope", "public employer evidence and NCS aggregate demand"), ("recruiter_profiles", "not available")])
        else:
            ncs = [r for r in rows(SOURCE_FILES["ncs"]) if r["metric"] in ("Jobseeker Registered", "Active Jobseekers")]
            rates = list(rows(SOURCE_FILES["rates"])); base = list(rows(SOURCE_FILES["baselines"]))
            agg = [{"metric": r["metric"], "geography": r["state"], "period": r["financial_year"], "value": r["value"], "source_url": r["source_url"], "quality_flag": r["quality_flag"]} for r in ncs]
            rate_fields = ["source_id","geography","year","year_type","frequency","quarter","month","indicator","value","unit","reference_status","role_scope","use","source_url"]
            rate_records = [{k: (text(r[k]) if k not in ("indicator", "unit", "role_scope", "use") else (text(r[k]) or "unspecified")) for k in rate_fields} for r in rates]
            base_fields = ["geography","year","year_type","frequency","quarter","month","reference_status","lfpr_percent","ur_percent","wpr_percent","implied_employed_per_100_population","available_data_analysts_estimate","role_scope","use","limitations"]
            base_records = [{k: (text(r.get(k)) if k not in ("role_scope", "use", "limitations") else (text(r.get(k)) or "unspecified")) for k in base_fields} for r in base]
            zero_fields = ["candidate_id","geography","profile_status","consent_reference","created_at"]; zero_skills = ["candidate_id","skill_id","evidence_type","proficiency"]
            counts[name] = {"candidate_profiles": insert_csv(con, folder, "candidate_profiles", zero_fields, []), "candidate_skills": insert_csv(con, folder, "candidate_skills", zero_skills, []), "aggregate_jobseekers": insert_csv(con, folder, "aggregate_jobseekers", list(agg[0]), agg), "labour_rates": insert_csv(con, folder, "labour_rates", rate_fields, rate_records), "workforce_baselines": insert_csv(con, folder, "workforce_baselines", base_fields, base_records)}
            con.executemany("INSERT INTO metadata VALUES (?,?)", [("scope", "official aggregate workforce evidence"), ("individual_jobseekers", "not available"), ("reliable_gap_or_forecast_ready", "false")])
        con.commit(); con.close()
    manifest = {"schema_version": 1, "source_files": source_hashes, "databases": {}, "readiness": {"individual_jobseekers_available": False, "reliable_gap_or_forecast_ready": False}}
    for name, _, folder in db_specs:
        manifest["databases"][name] = {"sha256": hashlib.sha256((output / name).read_bytes()).hexdigest(), "csv_folder": folder, "row_counts": counts[name]}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
