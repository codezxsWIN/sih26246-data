import json
import sqlite3
from typing import Dict, Any, List, Optional
from engine.config import settings
from engine.db.connection import get_db_connection
from engine.db.repositories import GapRepository, DemandRepository, SupplyRepository

class GapEngine:
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self.conn = conn or get_db_connection()
        self.repo = GapRepository(self.conn)
        self.demand_repo = DemandRepository(self.conn)
        self.supply_repo = SupplyRepository(self.conn)
        self.thresholds = settings.get_weights().get("shortage_risk_thresholds", {
            "critical_shortage": 75.0,
            "moderate_shortage": 55.0,
            "balanced": 40.0
        })

    def classify_risk(self, gap_score: float, gap_ratio: float) -> str:
        if gap_score >= self.thresholds["critical_shortage"] or gap_ratio >= 1.5:
            return "Critical Shortage"
        elif gap_score >= self.thresholds["moderate_shortage"] or gap_ratio >= 1.1:
            return "Moderate Shortage"
        elif gap_score >= self.thresholds["balanced"] or gap_ratio >= 0.8:
            return "Balanced"
        else:
            return "Oversupply"

    def calculate_gap(
        self,
        entity_name: str,
        entity_type: str = "occupation",
        geography_name: str = "All India",
        time_period: str = "2026-Q1"
    ) -> Dict[str, Any]:
        # Fetch or compute demand score
        d_scores = self.demand_repo.get_demand_scores(entity_type=entity_type, geography_name=geography_name, limit=500)
        d_score_val = 65.0
        d_match = [s for s in d_scores if s["entity_name"].lower() == entity_name.lower()]
        if d_match:
            d_score_val = d_match[0]["demand_score"]

        # Fetch or compute supply estimate
        s_estimates = self.supply_repo.get_supply_estimates(entity_type=entity_type, geography_name=geography_name, limit=500)
        s_val = 5000.0
        s_match = [s for s in s_estimates if s["entity_name"].lower() == entity_name.lower()]
        if s_match:
            s_val = s_match[0]["estimated_supply"]

        # Scaled supply benchmark for comparison (0-100 scale)
        scaled_supply = min(100.0, max(5.0, s_val / 200.0))
        gap_score = round(d_score_val - scaled_supply + 50.0, 2)
        gap_ratio = round(d_score_val / max(1.0, scaled_supply), 2)
        
        risk_category = self.classify_risk(gap_score, gap_ratio)

        # Explicit feature driver contributions
        drivers = {
            "demand_score_contribution": round(d_score_val * 0.60, 2),
            "supply_scarcity_contribution": round((100.0 - scaled_supply) * 0.30, 2),
            "historical_trend_contribution": 10.0
        }

        return {
            "entity_type": entity_type,
            "entity_name": entity_name,
            "geography_level": "state" if geography_name != "All India" else "national",
            "geography_name": geography_name,
            "time_period": time_period,
            "demand_score": round(d_score_val, 2),
            "supply_estimate": round(s_val, 2),
            "gap_score": gap_score,
            "gap_ratio": gap_ratio,
            "shortage_risk_category": risk_category,
            "shap_drivers_json": json.dumps(drivers)
        }

    def run_gap_pipeline(self, target_entities: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        entities = target_entities or [
            "Software Developer", "Data Analyst / Scientist", "AI/ML Specialist",
            "Web Developer", "Systems Administrator / DevOps", "Motor Vehicle Mechanic",
            "Electrician", "Solar Photovoltaic Installer", "Welder and Flame Cutter",
            "CNC Machine Operator", "Registered Nurse", "Pharmacist"
        ]
        geographies = ["All India", "Maharashtra", "Karnataka", "Tamil Nadu", "Gujarat", "Telangana"]
        
        gaps = []
        for ent in entities:
            for geo in geographies:
                gap = self.calculate_gap(ent, "occupation", geo, "2026-Q1")
                gaps.append(gap)
                
        self.repo.save_gaps(gaps)
        return gaps
