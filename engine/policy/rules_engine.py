import sqlite3
from typing import Dict, Any, List, Optional
from engine.db.connection import get_db_connection
from engine.db.repositories import PolicyRepository, GapRepository, DemandRepository

class PolicyRulesEngine:
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self.conn = conn or get_db_connection()
        self.repo = PolicyRepository(self.conn)
        self.gap_repo = GapRepository(self.conn)
        self.demand_repo = DemandRepository(self.conn)

    def evaluate_interventions_for_gap(self, gap_record: Dict[str, Any]) -> List[Dict[str, Any]]:
        interventions = []
        entity_name = gap_record["entity_name"]
        geo_name = gap_record["geography_name"]
        gap_score = gap_record["gap_score"]
        risk_cat = gap_record["shortage_risk_category"]
        d_score = gap_record["demand_score"]

        # RULE_01: Critical Shortage Capacity Surge
        if risk_cat == "Critical Shortage" or gap_score > 75.0:
            interventions.append({
                "trigger_rule_id": "RULE_01",
                "trigger_condition": f"Critical Shortage detected for {entity_name} in {geo_name} (Gap Score: {gap_score})",
                "target_state": geo_name,
                "target_sector": "High Priority Sector",
                "target_occupation": entity_name,
                "target_skill": f"{entity_name} Core Skills",
                "recommended_intervention": f"Emergency PMKVY & DGT ITI seat expansion (+50% capacity) for {entity_name} in {geo_name}",
                "priority_level": "HIGH",
                "estimated_capacity_needed": 2500,
                "cost_impact_estimate": "₹4.5 Cr State Budget Allocation"
            })

        # RULE_02: Moderate Shortage Apprenticeship Push
        if risk_cat == "Moderate Shortage" or (55.0 <= gap_score <= 75.0):
            interventions.append({
                "trigger_rule_id": "RULE_02",
                "trigger_condition": f"Moderate Shortage detected for {entity_name} in {geo_name}",
                "target_state": geo_name,
                "target_sector": "Industrial & Tech",
                "target_occupation": entity_name,
                "target_skill": f"{entity_name} Practical Competencies",
                "recommended_intervention": f"Launch NAPS/NATS employer stipend matching drive for {entity_name}",
                "priority_level": "MEDIUM",
                "estimated_capacity_needed": 1200,
                "cost_impact_estimate": "₹1.8 Cr Employer Subsidy"
            })

        # RULE_03: Green Skill Transition Incentive
        if any(term in entity_name.lower() for term in ["solar", "ev", "electric vehicle", "renewable", "wind"]):
            interventions.append({
                "trigger_rule_id": "RULE_03",
                "trigger_condition": f"Green Economy transition role identified: {entity_name}",
                "target_state": geo_name,
                "target_sector": "Renewable Energy & EV",
                "target_occupation": entity_name,
                "target_skill": "Solar PV Installation / EV Powertrain Maintenance",
                "recommended_intervention": f"Deploy NSTI specialized green curriculum module and 100% tuition subsidy for {entity_name}",
                "priority_level": "HIGH",
                "estimated_capacity_needed": 1500,
                "cost_impact_estimate": "₹2.5 Cr Green Transition Fund"
            })

        # RULE_04: High-Growth Tech Reskilling
        if d_score >= 70.0 and any(term in entity_name.lower() for term in ["data", "ai", "machine learning", "software", "devops"]):
            interventions.append({
                "trigger_rule_id": "RULE_04",
                "trigger_condition": f"High demand tech role (Score: {d_score}) for {entity_name}",
                "target_state": geo_name,
                "target_sector": "IT & Digital Economy",
                "target_occupation": entity_name,
                "target_skill": "Advanced AI/ML & Cloud Systems",
                "recommended_intervention": f"Establish University-Industry co-funded reskilling bootcamp for {entity_name}",
                "priority_level": "HIGH",
                "estimated_capacity_needed": 3000,
                "cost_impact_estimate": "₹5.0 Cr Co-Funded Model"
            })

        # RULE_05: Oversupply Retraining Shift
        if risk_cat == "Oversupply" or gap_score < 35.0:
            interventions.append({
                "trigger_rule_id": "RULE_05",
                "trigger_condition": f"Oversupply flagged for {entity_name} in {geo_name}",
                "target_state": geo_name,
                "target_sector": "Transitioning Sectors",
                "target_occupation": entity_name,
                "target_skill": "Adjacent High-Demand Skills",
                "recommended_intervention": f"Reallocate 30% of training subsidies from {entity_name} to critical shortage occupations",
                "priority_level": "LOW",
                "estimated_capacity_needed": 0,
                "cost_impact_estimate": "Budget Neutral / Reallocation"
            })

        return interventions

    def run_policy_engine(self) -> List[Dict[str, Any]]:
        gaps = self.gap_repo.get_gaps(limit=500)
        all_interventions = []
        for g in gaps:
            interventions = self.evaluate_interventions_for_gap(g)
            all_interventions.extend(interventions)
            
        if all_interventions:
            self.repo.save_policy_interventions(all_interventions)
            
        return all_interventions
