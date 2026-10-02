import sqlite3
import pandas as pd
from typing import Dict, Any, List
from engine.config import settings
from engine.db.connection import get_db_connection
from engine.db.schema import init_schema
from engine.ingest.normalizer import LocationNormalizer, NCOMapper, SkillExtractor

SEED_NCO_CODES = [
    ("2511.0100", "Data Analyst / Scientist", "25", "Information and Communications Technology Professionals", "251", "Software and Applications Developers", "Professionals", "Analytic data models and statistical inference", "2511"),
    ("2512.0100", "Software Developer", "25", "Information and Communications Technology Professionals", "251", "Software and Applications Developers", "Professionals", "Designs, develops, and tests software applications", "2512"),
    ("2512.0200", "AI/ML Specialist", "25", "Information and Communications Technology Professionals", "251", "Software and Applications Developers", "Professionals", "Builds artificial intelligence and machine learning pipelines", "2512"),
    ("2512.0300", "Web Developer", "25", "Information and Communications Technology Professionals", "251", "Software and Applications Developers", "Professionals", "Develops responsive web frontends and APIs", "2512"),
    ("2519.0100", "Systems Administrator / DevOps", "25", "Information and Communications Technology Professionals", "251", "Software and Applications Developers", "Professionals", "Cloud infrastructure and CI/CD operations", "2519"),
    ("7231.0100", "Motor Vehicle Mechanic", "72", "Machinery and Related Trades Workers", "723", "Machinery Mechanics and Fitters", "Craft & Related Trades", "Services and repairs combustion and EV powertrains", "7231"),
    ("7411.0100", "Electrician", "74", "Electrical and Electronic Trades Workers", "741", "Electrical Equipment Installers", "Craft & Related Trades", "Installs, tests, and maintains electrical wiring", "7411"),
    ("7411.0200", "Solar Photovoltaic Installer", "74", "Electrical and Electronic Trades Workers", "741", "Electrical Equipment Installers", "Craft & Related Trades", "Installs solar panels, inverters, and battery storage", "7411"),
    ("7212.0100", "Welder and Flame Cutter", "72", "Metal, Machinery and Related Trades", "721", "Sheet and Structural Metal Workers", "Craft & Related Trades", "Operates welding equipment to join metal parts", "7212"),
    ("7223.0100", "CNC Machine Operator", "72", "Metal, Machinery and Related Trades", "722", "Blacksmiths and Toolmakers", "Craft & Related Trades", "Sets up and operates CNC lathes and milling machines", "7223"),
    ("2221.0100", "Registered Nurse", "22", "Health Professionals", "222", "Nursing and Midwifery Professionals", "Professionals", "Provides direct patient healthcare in clinical settings", "2221"),
    ("2262.0100", "Pharmacist", "22", "Health Professionals", "226", "Other Health Professionals", "Professionals", "Dispenses prescription medications and monitors therapies", "2262")
]

SEED_JOB_POSTINGS = [
    {"job_title": "Senior Data Scientist", "company_name": "TCS Analytics", "location": "Pune, Maharashtra", "role_category": "Data Science", "skills_required": "Python, SQL, Machine Learning, TensorFlow, AWS", "experience_min": 3, "experience_max": 7, "salary_min": 12.0, "salary_max": 20.0, "posting_date": "2023-12-15", "data_source": "PromptCloud Dec 2023 Scrape"},
    {"job_title": "Full Stack Software Developer", "company_name": "Infosys Tech", "location": "Bengaluru, Karnataka", "role_category": "Software Engineering", "skills_required": "Java, React, Spring Boot, Docker, Git", "experience_min": 2, "experience_max": 5, "salary_min": 8.0, "salary_max": 15.0, "posting_date": "2023-12-18", "data_source": "PromptCloud Dec 2023 Scrape"},
    {"job_title": "AI/ML Engineer", "company_name": "Reliance Jio AI Labs", "location": "Mumbai, Maharashtra", "role_category": "Artificial Intelligence", "skills_required": "Python, PyTorch, Deep Learning, FastApi, Docker", "experience_min": 1, "experience_max": 4, "salary_min": 10.0, "salary_max": 18.0, "posting_date": "2023-12-20", "data_source": "Naukri Scrape"},
    {"job_title": "EV Battery Systems Technician", "company_name": "Tata Motors EV", "location": "Pune, Maharashtra", "role_category": "Automotive Engineering", "skills_required": "Electric Vehicle, Battery Management System, Quality Control, PLC", "experience_min": 2, "experience_max": 6, "salary_min": 6.0, "salary_max": 11.0, "posting_date": "2023-12-10", "data_source": "LinkedIn Job Scrape"},
    {"job_title": "Solar Energy Systems Installer", "company_name": "Adani Green Energy", "location": "Ahmedabad, Gujarat", "role_category": "Renewable Energy", "skills_required": "Solar Energy, Electrical Wiring, Safety Compliance", "experience_min": 0, "experience_max": 3, "salary_min": 3.5, "salary_max": 6.5, "posting_date": "2023-12-22", "data_source": "Naukri Scrape"},
    {"job_title": "DevOps & Cloud Engineer", "company_name": "Wipro Digital", "location": "Hyderabad, Telangana", "role_category": "Cloud Infrastructure", "skills_required": "AWS, Kubernetes, Linux, Docker, Python", "experience_min": 3, "experience_max": 8, "salary_min": 14.0, "salary_max": 24.0, "posting_date": "2023-12-28", "data_source": "LinkedIn Job Scrape"},
    {"job_title": "CNC Machine Operator & Tooling Lead", "company_name": "Bharat Forge", "location": "Pune, Maharashtra", "role_category": "Manufacturing", "skills_required": "CNC Programming, AutoCAD, ISO 9001, Quality Control", "experience_min": 4, "experience_max": 9, "salary_min": 5.0, "salary_max": 9.5, "posting_date": "2023-12-05", "data_source": "Naukri Scrape"}
]

SEED_HISTORICAL_UNEMPLOYMENT = [
    {"state": "Maharashtra", "period": "2023-01", "year": 2023, "month": 1, "lfpr_percent": 42.5, "ur_percent": 4.8, "wpr_percent": 40.5, "estimated_employed": 24500000, "estimated_unemployed": 1234000, "data_source": "Unemployment in India Dataset"},
    {"state": "Maharashtra", "period": "2023-02", "year": 2023, "month": 2, "lfpr_percent": 42.8, "ur_percent": 4.6, "wpr_percent": 40.8, "estimated_employed": 24650000, "estimated_unemployed": 1190000, "data_source": "Unemployment in India Dataset"},
    {"state": "Maharashtra", "period": "2023-03", "year": 2023, "month": 3, "lfpr_percent": 43.1, "ur_percent": 4.5, "wpr_percent": 41.2, "estimated_employed": 24800000, "estimated_unemployed": 1170000, "data_source": "Unemployment in India Dataset"},
    {"state": "Maharashtra", "period": "2023-06", "year": 2023, "month": 6, "lfpr_percent": 43.5, "ur_percent": 4.3, "wpr_percent": 41.6, "estimated_employed": 25100000, "estimated_unemployed": 1128000, "data_source": "Unemployment in India Dataset"},
    {"state": "Maharashtra", "period": "2023-12", "year": 2023, "month": 12, "lfpr_percent": 44.0, "ur_percent": 4.1, "wpr_percent": 42.2, "estimated_employed": 25400000, "estimated_unemployed": 1087000, "data_source": "Unemployment in India Dataset"},
    {"state": "Karnataka", "period": "2023-12", "year": 2023, "month": 12, "lfpr_percent": 45.2, "ur_percent": 3.8, "wpr_percent": 43.5, "estimated_employed": 18900000, "estimated_unemployed": 745000, "data_source": "Unemployment in India Dataset"},
    {"state": "Tamil Nadu", "period": "2023-12", "year": 2023, "month": 12, "lfpr_percent": 46.0, "ur_percent": 4.2, "wpr_percent": 44.1, "estimated_employed": 21200000, "estimated_unemployed": 929000, "data_source": "Unemployment in India Dataset"}
]

class ExternalDataLoader:
    def __init__(self, conn: sqlite3.Connection = None):
        self.conn = conn or get_db_connection()
        init_schema(self.conn)

    def seed_nco_taxonomy(self) -> int:
        cursor = self.conn.cursor()
        sql = """
        INSERT OR IGNORE INTO nco_taxonomy (
            nco_code, nco_title, division_code, division_title, sub_major_code,
            sub_major_title, major_group, description, isco_code
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        cursor.executemany(sql, SEED_NCO_CODES)
        self.conn.commit()
        return len(SEED_NCO_CODES)

    def seed_job_postings(self) -> int:
        cursor = self.conn.cursor()
        count = 0
        for job in SEED_JOB_POSTINGS:
            state, district = LocationNormalizer.normalize(job["location"])
            nco_code, canonical_role = NCOMapper.map_title_to_nco(job["job_title"])
            
            cursor.execute(
                """
                INSERT INTO raw_job_postings (
                    job_title, company_name, location, state, district, role_category,
                    nco_code, skills_required, experience_min, experience_max,
                    salary_min, salary_max, salary_disclosed, posting_date, data_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job["job_title"], job["company_name"], job["location"], state, district,
                    canonical_role, nco_code, job["skills_required"], job["experience_min"],
                    job["experience_max"], job["salary_min"], job["salary_max"], 1,
                    job["posting_date"], job["data_source"]
                )
            )
            count += 1
            
        self.conn.commit()
        return count

    def seed_historical_unemployment(self) -> int:
        cursor = self.conn.cursor()
        count = 0
        for row in SEED_HISTORICAL_UNEMPLOYMENT:
            cursor.execute(
                """
                INSERT INTO historical_labour_metrics (
                    state, period, year, month, lfpr_percent, ur_percent, wpr_percent,
                    estimated_employed, estimated_unemployed, data_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["state"], row["period"], row["year"], row["month"],
                    row["lfpr_percent"], row["ur_percent"], row["wpr_percent"],
                    row["estimated_employed"], row["estimated_unemployed"], row["data_source"]
                )
            )
            count += 1
            
        self.conn.commit()
        return count

    def run_all(self) -> Dict[str, int]:
        nco_count = self.seed_nco_taxonomy()
        postings_count = self.seed_job_postings()
        hist_count = self.seed_historical_unemployment()
        return {
            "nco_codes_seeded": nco_count,
            "job_postings_seeded": postings_count,
            "historical_unemployment_seeded": hist_count
        }
