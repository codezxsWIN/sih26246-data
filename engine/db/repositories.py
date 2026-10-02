import json
import sqlite3
from typing import List, Dict, Any, Optional
from engine.db.connection import get_db_connection

class DemandRepository:
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self.conn = conn or get_db_connection()

    def save_demand_scores(self, scores: List[Dict[str, Any]]) -> None:
        cursor = self.conn.cursor()
        sql = """
        INSERT INTO demand_scores (
            entity_type, entity_name, geography_level, geography_name, time_period,
            demand_score, posting_growth_component, employer_component, plfs_component,
            ncs_component, vacancy_volume_component, confidence_interval_lower,
            confidence_interval_upper, data_quality_grade
        ) VALUES (
            :entity_type, :entity_name, :geography_level, :geography_name, :time_period,
            :demand_score, :posting_growth_component, :employer_component, :plfs_component,
            :ncs_component, :vacancy_volume_component, :confidence_interval_lower,
            :confidence_interval_upper, :data_quality_grade
        );
        """
        cursor.executemany(sql, scores)
        self.conn.commit()

    def get_demand_scores(
        self,
        entity_type: Optional[str] = None,
        geography_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        query = "SELECT * FROM demand_scores WHERE 1=1"
        params = []
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        if geography_name:
            query += " AND geography_name = ?"
            params.append(geography_name)
        query += " ORDER BY demand_score DESC LIMIT ?"
        params.append(limit)
        
        rows = cursor.execute(query, params).fetchall()
        return [dict(row) for row in rows]

class SupplyRepository:
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self.conn = conn or get_db_connection()

    def save_supply_estimates(self, estimates: List[Dict[str, Any]]) -> None:
        cursor = self.conn.cursor()
        sql = """
        INSERT INTO supply_estimates (
            entity_type, entity_name, geography_level, geography_name, time_period,
            estimated_supply, education_flow, training_flow, plfs_unemployed_baseline,
            lower_bound, upper_bound, confidence_interval, data_sources_used
        ) VALUES (
            :entity_type, :entity_name, :geography_level, :geography_name, :time_period,
            :estimated_supply, :education_flow, :training_flow, :plfs_unemployed_baseline,
            :lower_bound, :upper_bound, :confidence_interval, :data_sources_used
        );
        """
        cursor.executemany(sql, estimates)
        self.conn.commit()

    def get_supply_estimates(
        self,
        entity_type: Optional[str] = None,
        geography_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        query = "SELECT * FROM supply_estimates WHERE 1=1"
        params = []
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        if geography_name:
            query += " AND geography_name = ?"
            params.append(geography_name)
        query += " ORDER BY estimated_supply DESC LIMIT ?"
        params.append(limit)
        
        rows = cursor.execute(query, params).fetchall()
        return [dict(row) for row in rows]

class GapRepository:
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self.conn = conn or get_db_connection()

    def save_gaps(self, gaps: List[Dict[str, Any]]) -> None:
        cursor = self.conn.cursor()
        sql = """
        INSERT INTO demand_supply_gaps (
            entity_type, entity_name, geography_level, geography_name, time_period,
            demand_score, supply_estimate, gap_score, gap_ratio, shortage_risk_category, shap_drivers_json
        ) VALUES (
            :entity_type, :entity_name, :geography_level, :geography_name, :time_period,
            :demand_score, :supply_estimate, :gap_score, :gap_ratio, :shortage_risk_category, :shap_drivers_json
        );
        """
        cursor.executemany(sql, gaps)
        self.conn.commit()

    def get_gaps(
        self,
        risk_category: Optional[str] = None,
        geography_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        query = "SELECT * FROM demand_supply_gaps WHERE 1=1"
        params = []
        if risk_category:
            query += " AND shortage_risk_category = ?"
            params.append(risk_category)
        if geography_name:
            query += " AND geography_name = ?"
            params.append(geography_name)
        query += " ORDER BY gap_score DESC LIMIT ?"
        params.append(limit)
        
        rows = cursor.execute(query, params).fetchall()
        return [dict(row) for row in rows]

class ForecastRepository:
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self.conn = conn or get_db_connection()

    def save_forecasts(self, forecasts: List[Dict[str, Any]]) -> None:
        cursor = self.conn.cursor()
        sql = """
        INSERT INTO forecasts (
            entity_type, entity_name, geography_name, forecast_horizon_months,
            model_type, predicted_demand_score, baseline_demand_score, lower_bound,
            upper_bound, feature_importance_json
        ) VALUES (
            :entity_type, :entity_name, :geography_name, :forecast_horizon_months,
            :model_type, :predicted_demand_score, :baseline_demand_score, :lower_bound,
            :upper_bound, :feature_importance_json
        );
        """
        cursor.executemany(sql, forecasts)
        self.conn.commit()

    def get_forecasts(
        self,
        entity_name: Optional[str] = None,
        horizon_months: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        query = "SELECT * FROM forecasts WHERE 1=1"
        params = []
        if entity_name:
            query += " AND entity_name = ?"
            params.append(entity_name)
        if horizon_months:
            query += " AND forecast_horizon_months = ?"
            params.append(horizon_months)
        query += " ORDER BY predicted_demand_score DESC LIMIT ?"
        params.append(limit)
        
        rows = cursor.execute(query, params).fetchall()
        return [dict(row) for row in rows]

class PolicyRepository:
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self.conn = conn or get_db_connection()

    def save_policy_interventions(self, interventions: List[Dict[str, Any]]) -> None:
        cursor = self.conn.cursor()
        sql = """
        INSERT INTO policy_interventions (
            trigger_rule_id, trigger_condition, target_state, target_sector,
            target_occupation, target_skill, recommended_intervention, priority_level,
            estimated_capacity_needed, cost_impact_estimate
        ) VALUES (
            :trigger_rule_id, :trigger_condition, :target_state, :target_sector,
            :target_occupation, :target_skill, :recommended_intervention, :priority_level,
            :estimated_capacity_needed, :cost_impact_estimate
        );
        """
        cursor.executemany(sql, interventions)
        self.conn.commit()

    def get_interventions(
        self,
        priority_level: Optional[str] = None,
        target_state: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        query = "SELECT * FROM policy_interventions WHERE 1=1"
        params = []
        if priority_level:
            query += " AND priority_level = ?"
            params.append(priority_level)
        if target_state:
            query += " AND target_state = ?"
            params.append(target_state)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        
        rows = cursor.execute(query, params).fetchall()
        return [dict(row) for row in rows]
