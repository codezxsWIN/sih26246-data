import sqlite3
import pandas as pd
from typing import Dict, Any
from engine.config import settings
from engine.db.connection import get_db_connection
from engine.db.schema import init_schema
from engine.ingest.normalizer import LocationNormalizer, NCOMapper, SkillExtractor

class BaseDataLoader:
    def __init__(self, conn: sqlite3.Connection = None):
        self.conn = conn or get_db_connection()
        init_schema(self.conn)

    def load_ncs_metrics(self) -> int:
        ncs_csv = settings.ROOT_DIR / "DATA_100PLUS" / "20261002-v6" / "ncs_state_year_metrics.csv"
        if not ncs_csv.exists():
            return 0
            
        df = pd.read_csv(ncs_csv)
        cursor = self.conn.cursor()
        
        count = 0
        for _, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO historical_labour_metrics (
                    state, period, year, month, lfpr_percent, ur_percent, wpr_percent,
                    estimated_employed, estimated_unemployed, data_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("state", "All India"),
                    str(row.get("financial_year", "FY 2025-26")),
                    2025,
                    1,
                    None,
                    None,
                    None,
                    int(row["value"]) if row.get("metric") == "Active Jobseekers" and pd.notnull(row.get("value")) else None,
                    None,
                    "NCS State Metrics"
                )
            )
            count += 1
            
        self.conn.commit()
        return count

    def load_plfs_rates(self) -> int:
        plfs_csv = settings.ROOT_DIR / "DATA_100PLUS" / "20261002-v6" / "plfs_workforce_rates.csv"
        if not plfs_csv.exists():
            return 0
            
        df = pd.read_csv(plfs_csv)
        cursor = self.conn.cursor()
        
        count = 0
        for _, row in df.iterrows():
            state = row.get("geography", "All India")
            period = str(row.get("year", "2023-24"))
            indicator = str(row.get("indicator", "")).upper()
            val = float(row["value"]) if pd.notnull(row.get("value")) else None
            
            lfpr = val if "LFPR" in indicator else None
            ur = val if "UR" in indicator or "UNEMPLOYMENT" in indicator else None
            wpr = val if "WPR" in indicator else None
            
            cursor.execute(
                """
                INSERT INTO historical_labour_metrics (
                    state, period, year, month, lfpr_percent, ur_percent, wpr_percent,
                    estimated_employed, estimated_unemployed, data_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (state, period, 2024, 1, lfpr, ur, wpr, None, None, "PLFS MoSPI")
            )
            count += 1
            
        self.conn.commit()
        return count

    def run_all(self) -> Dict[str, int]:
        ncs_count = self.load_ncs_metrics()
        plfs_count = self.load_plfs_rates()
        return {
            "ncs_metrics_loaded": ncs_count,
            "plfs_rates_loaded": plfs_count
        }
