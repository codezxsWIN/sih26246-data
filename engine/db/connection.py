import sqlite3
from pathlib import Path
from typing import Optional
from engine.config import settings
from engine.db.schema import init_schema

def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    target_path = db_path or settings.ENGINE_DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(target_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    # Apply performance & WAL pragmas
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    
    return conn

def init_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    conn = get_db_connection(db_path)
    init_schema(conn)
    return conn
