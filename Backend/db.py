"""
Shared Database Module - Centralized MySQL Connection Pool
Provides thread-safe connection pooling and cursor context managers.
"""

import os
from contextlib import contextmanager
import mysql.connector
from mysql.connector import pooling, Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database credentials configuration
DB_HOST = os.getenv("DB_HOST") or os.getenv("TIDB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT") or os.getenv("TIDB_PORT", 3306))
DB_USER = os.getenv("DB_USER") or os.getenv("TIDB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("TIDB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME") or os.getenv("TIDB_DATABASE", "test")
DB_POOL_NAME = os.getenv("DB_POOL_NAME", "texas_db_pool")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))
DB_SSL_CA = os.getenv("DB_SSL_CA", "")

_pool = None

def init_connection_pool():
    """Initializes the MySQL connection pool singleton."""
    global _pool
    if _pool is not None:
        return _pool

    db_config = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "database": DB_NAME,
        "pool_name": DB_POOL_NAME,
        "pool_size": DB_POOL_SIZE,
        "autocommit": False,
        "charset": "utf8mb4",
        "collation": "utf8mb4_unicode_ci"
    }

    # If SSL CA cert is provided and exists, add SSL config
    if DB_SSL_CA and os.path.exists(DB_SSL_CA):
        db_config["ssl_ca"] = DB_SSL_CA
        db_config["ssl_verify_cert"] = True
    elif "tidbcloud.com" in DB_HOST.lower():
        # TiDB cloud requires SSL
        db_config["ssl_verify_cert"] = False
        db_config["ssl_disabled"] = False

    try:
        _pool = pooling.MySQLConnectionPool(**db_config)
        print(f"[DB] Initialized connection pool '{DB_POOL_NAME}' (Size: {DB_POOL_SIZE}) for host {DB_HOST}:{DB_PORT}")
        return _pool
    except Error as err:
        print(f"[DB Error] Failed to initialize connection pool: {err}")
        # If pool creation fails with existing pool name, try getting existing
        try:
            _pool = pooling.MySQLConnectionPool(pool_name=DB_POOL_NAME)
            return _pool
        except Exception:
            raise err

def get_db_connection():
    """Retrieves a connection from the connection pool."""
    global _pool
    if _pool is None:
        init_connection_pool()
    return _pool.get_connection()

@contextmanager
def get_db_cursor(dictionary=True, commit=True):
    """
    Context manager for database cursor with automatic transaction management.
    Yields (cursor, connection) or cursor.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def check_db_health():
    """Health check helper to test database connectivity."""
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT 1 AS status;")
            result = cursor.fetchone()
            return {"status": "healthy", "database": DB_NAME, "host": DB_HOST, "result": result}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "database": DB_NAME, "host": DB_HOST}
