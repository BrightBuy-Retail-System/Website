import os
from contextlib import contextmanager
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

load_dotenv()

TIDB_HOST = os.getenv("TIDB_HOST")
TIDB_PORT = int(os.getenv("TIDB_PORT", 4000))
TIDB_USER = os.getenv("TIDB_USER")
TIDB_PASSWORD = os.getenv("TIDB_PASSWORD")
TIDB_DATABASE = os.getenv("TIDB_DATABASE", "test")

def get_connection():
    """Establish a connection to the TiDB database"""
    return pymysql.connect(
        host=TIDB_HOST,
        port=TIDB_PORT,
        user=TIDB_USER,
        password=TIDB_PASSWORD,
        database=TIDB_DATABASE,
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        cursorclass=DictCursor,
        autocommit=False,
        connect_timeout=10
    )

@contextmanager
def get_db_cursor():
    """Context manager for obtaining a database cursor with automatic transaction management"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def init_db():
    """Initialize database tables if they do not exist"""
    create_users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL UNIQUE,
        hashed_password VARCHAR(255) NOT NULL,
        phonenum VARCHAR(20) NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(create_users_table_sql)
        print(" Database tables initialized in TiDB successfully!")
    except Exception as e:
        print(f" Failed to initialize database: {e}")