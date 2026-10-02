import sqlite3
from typing import List

CREATE_SCHEMA_SQL: List[str] = [
    """
    CREATE TABLE IF NOT EXISTS raw_job_postings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT NOT NULL,
        company_name TEXT,
        location TEXT,
        state TEXT,
        district TEXT,
        role_category TEXT,
        nco_code TEXT,
        skills_required TEXT,
        experience_min REAL,
        experience_max REAL,
        salary_min REAL,
        salary_max REAL,
        salary_disclosed BOOLEAN DEFAULT 0,
        posting_date TEXT,
        data_source TEXT,
        raw_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS nco_taxonomy (
        nco_code TEXT PRIMARY KEY,
        nco_title TEXT NOT NULL,
        division_code TEXT,
        division_title TEXT,
        sub_major_code TEXT,
        sub_major_title TEXT,
        major_group TEXT,
        description TEXT,
        isco_code TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS historical_labour_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state TEXT NOT NULL,
        period TEXT NOT NULL,
        year INTEGER,
        month INTEGER,
        lfpr_percent REAL,
        ur_percent REAL,
        wpr_percent REAL,
        estimated_employed INTEGER,
        estimated_unemployed INTEGER,
        data_source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS sectoral_economic_indicators (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sector_name TEXT NOT NULL,
        gva_growth_rate REAL,
        employment_share REAL,
        wage_index REAL,
        year INTEGER,
        data_source TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS demand_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL, -- 'occupation', 'skill', 'sector'
        entity_name TEXT NOT NULL,
        geography_level TEXT DEFAULT 'state', -- 'state', 'national', 'district'
        geography_name TEXT DEFAULT 'All India',
        time_period TEXT NOT NULL,
        demand_score REAL NOT NULL,
        posting_growth_component REAL,
        employer_component REAL,
        plfs_component REAL,
        ncs_component REAL,
        vacancy_volume_component REAL,
        confidence_interval_lower REAL,
        confidence_interval_upper REAL,
        data_quality_grade TEXT DEFAULT 'A',
        calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS supply_estimates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL,
        entity_name TEXT NOT NULL,
        geography_level TEXT DEFAULT 'state',
        geography_name TEXT DEFAULT 'All India',
        time_period TEXT NOT NULL,
        estimated_supply REAL NOT NULL,
        education_flow INTEGER DEFAULT 0,
        training_flow INTEGER DEFAULT 0,
        plfs_unemployed_baseline INTEGER DEFAULT 0,
        lower_bound REAL,
        upper_bound REAL,
        confidence_interval REAL,
        data_sources_used TEXT,
        calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS demand_supply_gaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL,
        entity_name TEXT NOT NULL,
        geography_level TEXT DEFAULT 'state',
        geography_name TEXT DEFAULT 'All India',
        time_period TEXT NOT NULL,
        demand_score REAL NOT NULL,
        supply_estimate REAL NOT NULL,
        gap_score REAL NOT NULL,
        gap_ratio REAL NOT NULL,
        shortage_risk_category TEXT NOT NULL, -- 'Critical Shortage', 'Moderate Shortage', 'Balanced', 'Oversupply'
        shap_drivers_json TEXT,
        calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS forecasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL,
        entity_name TEXT NOT NULL,
        geography_name TEXT DEFAULT 'All India',
        forecast_horizon_months INTEGER NOT NULL, -- 3, 6, 12
        model_type TEXT NOT NULL, -- 'ARIMA', 'XGBoost', 'Hybrid'
        predicted_demand_score REAL NOT NULL,
        baseline_demand_score REAL NOT NULL,
        lower_bound REAL,
        upper_bound REAL,
        feature_importance_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS policy_interventions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trigger_rule_id TEXT NOT NULL,
        trigger_condition TEXT NOT NULL,
        target_state TEXT DEFAULT 'All India',
        target_sector TEXT,
        target_occupation TEXT,
        target_skill TEXT,
        recommended_intervention TEXT NOT NULL,
        priority_level TEXT NOT NULL, -- 'HIGH', 'MEDIUM', 'LOW'
        estimated_capacity_needed INTEGER,
        cost_impact_estimate TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
]

CREATE_INDEXES_SQL: List[str] = [
    "CREATE INDEX IF NOT EXISTS idx_postings_state ON raw_job_postings(state);",
    "CREATE INDEX IF NOT EXISTS idx_postings_role ON raw_job_postings(role_category);",
    "CREATE INDEX IF NOT EXISTS idx_postings_nco ON raw_job_postings(nco_code);",
    "CREATE INDEX IF NOT EXISTS idx_demand_entity ON demand_scores(entity_type, entity_name, geography_name);",
    "CREATE INDEX IF NOT EXISTS idx_supply_entity ON supply_estimates(entity_type, entity_name, geography_name);",
    "CREATE INDEX IF NOT EXISTS idx_gap_risk ON demand_supply_gaps(shortage_risk_category);",
    "CREATE INDEX IF NOT EXISTS idx_forecast_horizon ON forecasts(entity_name, forecast_horizon_months);"
]

def init_schema(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    for statement in CREATE_SCHEMA_SQL:
        cursor.execute(statement)
    for index_stmt in CREATE_INDEXES_SQL:
        cursor.execute(index_stmt)
    conn.commit()
