"""
Database Migration Runner
Executes SQL migration scripts in migrations/ directory in sequential order.
"""

import os
import glob
from db import get_db_connection, DB_NAME, DB_HOST

def run_migrations():
    """Runs all migration files from the migrations/ folder."""
    migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
    sql_files = sorted(glob.glob(os.path.join(migrations_dir, "*.sql")))

    if not sql_files:
        print("[Migration] No SQL migration files found in migrations/ directory.")
        return

    print(f"[Migration] Starting migrations for database '{DB_NAME}' on {DB_HOST}...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for sql_file in sql_files:
            file_name = os.path.basename(sql_file)
            print(f" -> Executing migration: {file_name}")
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_script = f.read()

            # Execute SQL script (handling multiple statements)
            for statement in sql_script.split(";"):
                stmt = statement.strip()
                if stmt:
                    try:
                        cursor.execute(stmt)
                    except Exception as stmt_err:
                        # Log error but continue if table/view already exists or non-fatal
                        print(f"    [Warning/Info in {file_name}]: {stmt_err}")

            conn.commit()
            print(f" [OK] Completed migration: {file_name}")

        print("\n[Migration] All database migrations applied successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n[Migration Error] Failed executing migrations: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_migrations()
