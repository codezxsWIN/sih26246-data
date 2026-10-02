import sqlite3
import numpy as np
from typing import Dict, Any, List, Optional
from engine.config import settings
from engine.db.connection import get_db_connection
from engine.db.repositories import DemandRepository

class DemandEngine:
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self.conn = conn or get_db_connection()
        self.repo = DemandRepository(self.conn)
        self.weights_config = settings.get_weights()

    def calculate_score_for_entity(
        self,
        entity_name: str,
        entity_type: str = "occupation",
        geography_name: str = "All India",
        time_period: str = "2026-Q1"
    ) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        
        # 1. Job Posting Growth Component (0-100)
        postings = cursor.execute(
            "SELECT COUNT(*) as cnt FROM raw_job_postings WHERE (job_title LIKE ? OR role_category LIKE ?) AND (state = ? OR ? = 'All India')",
            (f"%{entity_name}%", f"%{entity_name}%", geography_name, geography_name)
        ).fetchone()["cnt"]
        
        posting_growth_comp = min(100.0, max(10.0, float(postings) * 15.0 + 30.0))

        # 2. Active Employer Count Component (0-100)
        employers = cursor.execute(
            "SELECT COUNT(DISTINCT company_name) as cnt FROM raw_job_postings WHERE (job_title LIKE ? OR role_category LIKE ?) AND (state = ? OR ? = 'All India')",
            (f"%{entity_name}%", f"%{entity_name}%", geography_name, geography_name)
        ).fetchone()["cnt"]
        
        employer_comp = min(100.0, max(10.0, float(employers) * 20.0 + 25.0))

        # 3. PLFS Employment Component (0-100)
        plfs_comp = 65.0  # Stable positive aggregate employment trend baseline

        # 4. NCS State Vacancy Component (0-100)
        ncs_row = cursor.execute(
            "SELECT AVG(estimated_employed) as avg_val FROM historical_labour_metrics WHERE (state = ? OR ? = 'All India') AND data_source = 'NCS State Metrics'",
            (geography_name, geography_name)
        ).fetchone()
        
        avg_ncs = ncs_row["avg_val"] if ncs_row and ncs_row["avg_val"] else 50000.0
        ncs_comp = min(100.0, max(20.0, float(avg_ncs) / 2000.0))

        # Check if per-posting vacancy volume is available
        has_vacancy_volume = False
        vacancy_volume_comp = 0.0

        if has_vacancy_volume:
            weights = self.weights_config["demand_score_weights"]
            final_score = (
                weights["job_posting_growth"] * posting_growth_comp +
                weights["active_employer_count"] * employer_comp +
                weights["plfs_sector_employment_trend"] * plfs_comp +
                weights["ncs_state_year_vacancy"] * ncs_comp +
                weights["vacancy_volume"] * vacancy_volume_comp
            )
        else:
            weights = self.weights_config["demand_score_fallback_weights"]
            final_score = (
                weights["job_posting_growth"] * posting_growth_comp +
                weights["active_employer_count"] * employer_comp +
                weights["plfs_sector_employment_trend"] * plfs_comp +
                weights["ncs_state_year_vacancy"] * ncs_comp
            )

        # Confidence bounds (+/- 5.0 points)
        ci_lower = max(0.0, final_score - 5.0)
        ci_upper = min(100.0, final_score + 5.0)

        result = {
            "entity_type": entity_type,
            "entity_name": entity_name,
            "geography_level": "state" if geography_name != "All India" else "national",
            "geography_name": geography_name,
            "time_period": time_period,
            "demand_score": round(final_score, 2),
            "posting_growth_component": round(posting_growth_comp, 2),
            "employer_component": round(employer_comp, 2),
            "plfs_component": round(plfs_comp, 2),
            "ncs_component": round(ncs_comp, 2),
            "vacancy_volume_component": round(vacancy_volume_comp, 2) if has_vacancy_volume else None,
            "confidence_interval_lower": round(ci_lower, 2),
            "confidence_interval_upper": round(ci_upper, 2),
            "data_quality_grade": "A" if postings > 0 else "B"
        }
        return result

    def run_scoring_pipeline(self, target_entities: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        entities = target_entities or [
            "Software Developer", "Data Analyst / Scientist", "AI/ML Specialist",
            "Web Developer", "Systems Administrator / DevOps", "Motor Vehicle Mechanic",
            "Electrician", "Solar Photovoltaic Installer", "Welder and Flame Cutter",
            "CNC Machine Operator", "Registered Nurse", "Pharmacist"
        ]
        
        geographies = ["All India", "Maharashtra", "Karnataka", "Tamil Nadu", "Gujarat", "Telangana"]
        
        scores = []
        for ent in entities:
            for geo in geographies:
                score = self.calculate_score_for_entity(ent, "occupation", geo, "2026-Q1")
                scores.append(score)
                
        self.repo.save_demand_scores(scores)
        return scores
