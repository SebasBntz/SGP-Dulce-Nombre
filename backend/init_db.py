import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
from dotenv import load_dotenv

# Load .env
BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")

# Settings from ENV
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "123456")
DB_SERVER = os.getenv("POSTGRES_SERVER", "127.0.0.1")
DB_NAME = os.getenv("POSTGRES_DB", "parroquia_db")

PROJECT_ROOT = BACKEND_DIR.parent
SCHEMA_FILE = PROJECT_ROOT / "database" / "schema.sql"

def init_db():
    print(f"--- INITIALIZING PARROQUIA DATABASE (PostgreSQL) ---")
    
    # 1. Connect to default postgres to create the new DB
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_SERVER,
            port="5432",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"Database '{DB_NAME}' already exists. Recreating...")
            try:
                cursor.execute(f"DROP DATABASE {DB_NAME} (FORCE)")
            except:
                # Fallback if FORCE is not supported (PostgreSQL < 13)
                cursor.execute(f"DROP DATABASE {DB_NAME}")
        
        print(f"Creating database '{DB_NAME}'...")
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting to PostgreSQL or creating DB: {e}")
        return

    # 2. Connect to the new DB and run schema
    try:
        print(f"Connecting to '{DB_NAME}' to apply schema...")
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_SERVER,
            port="5432",
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        if SCHEMA_FILE.exists():
            print(f"Applying schema from {SCHEMA_FILE}...")
            with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
                # PostgreSQL schema
                cursor.execute(schema_sql)
            conn.commit()
            print("Schema applied successfully.")
        else:
            print(f"Warning: Schema file not found at {SCHEMA_FILE}")
            
        cursor.close()
        conn.close()
        print("Database initialization successful.")
    except Exception as e:
        print(f"Error applying schema: {e}")

if __name__ == "__main__":
    init_db()
