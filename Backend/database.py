from pymysql import connections
import pymysql
from pymysql.cursors import DictCursor
import os
from dotenv import load_dotenv

load_dotenv()

TIDB_HOST = os.getenv("TIDB_HOST")
TIDB_PORT = int(os.getenv("TIDB_PORT", 4000))
TIDB_USER = os.getenv("TIDB_USER")
TIDB_PASSWORD = os.getenv("TIDB_PASSWORD")
TIDB_DATABASE = os.getenv("TIDB_DATABASE")

def get_connection():
    return pymysql.connect(
        host=TIDB_HOST,
        port=TIDB_PORT,
        user=TIDB_USER,
        password=TIDB_PASSWORD,
        database=TIDB_DATABASE,
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        cursorclass=DictCursor,
        autocommit=False
    )

def get_db_cursor():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def init_db():
    create_users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL UNIQUE,
        hashed_password VARCHAR(255) NOT NULL,
        phonenum VARCHAR(10) NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ); 
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(create_users_table_sql)
        conn.commit()
        print("✅ Raw SQL tables initialized in TiDB Cloud successfully!")
    finally:
        cursor.close()
        conn.close()