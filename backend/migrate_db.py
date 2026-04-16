import os
import psycopg2
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

def migrate():
    print(f"--- MIGRATING PARROQUIA DATABASE (PostgreSQL) ---")
    
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_SERVER,
            port="5432",
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # 1. Create Perfiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS perfiles (
                id_perfil SERIAL PRIMARY KEY,
                nombre_perfil VARCHAR(100) NOT NULL
            );
        """)

        # 2. Update Usuarios
        print("Updating 'usuarios' table...")
        cursor.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS usuario VARCHAR(50) UNIQUE;")
        cursor.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS clave VARCHAR(255);")
        cursor.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS id_perfil INTEGER REFERENCES perfiles(id_perfil);")
        cursor.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;")
        cursor.execute("ALTER TABLE usuarios ALTER COLUMN nombre_completo DROP NOT NULL;")
        cursor.execute("ALTER TABLE usuarios ALTER COLUMN email DROP NOT NULL;")
        cursor.execute("ALTER TABLE usuarios ALTER COLUMN password_hash DROP NOT NULL;")

        # 3. Create Personas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personas (
                id_persona SERIAL PRIMARY KEY,
                nombres VARCHAR(255) NOT NULL,
                apellidos VARCHAR(255) NOT NULL,
                fecha_nacimiento DATE,
                direccion VARCHAR(255),
                telefono VARCHAR(50),
                email VARCHAR(255),
                fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 4. Create Sacerdotes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sacerdotes (
                id_sacerdote SERIAL PRIMARY KEY,
                nombres VARCHAR(255) NOT NULL,
                apellidos VARCHAR(255) NOT NULL,
                telefono VARCHAR(50),
                email VARCHAR(255)
            );
        """)

        # 5. Create TiposSacramento
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tipos_sacramento (
                id_tipo SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL
            );
        """)

        # 6. Create Sacramentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sacramentos (
                id_sacramento SERIAL PRIMARY KEY,
                id_persona INTEGER REFERENCES personas(id_persona),
                id_tipo INTEGER REFERENCES tipos_sacramento(id_tipo),
                id_sacerdote INTEGER REFERENCES sacerdotes(id_sacerdote),
                fecha DATE,
                observaciones TEXT
            );
        """)

        # 7. Create Grupos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grupos (
                id_grupo SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT
            );
        """)

        # 8. Create GrupoPersona
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grupo_persona (
                id_grupo INTEGER REFERENCES grupos(id_grupo),
                id_persona INTEGER REFERENCES personas(id_persona),
                fecha_ingreso DATE DEFAULT CURRENT_DATE,
                PRIMARY KEY (id_grupo, id_persona)
            );
        """)

        # 9. Create GrupoAportes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grupo_aportes (
                id_grupo_aporte SERIAL PRIMARY KEY,
                id_grupo INTEGER REFERENCES grupos(id_grupo),
                id_persona INTEGER REFERENCES personas(id_persona),
                monto NUMERIC(12, 2),
                fecha DATE,
                tipo VARCHAR(50)
            );
        """)

        # 10. Create Aportes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aportes (
                id_aporte SERIAL PRIMARY KEY,
                id_persona INTEGER REFERENCES personas(id_persona),
                monto NUMERIC(12, 2),
                fecha DATE,
                tipo VARCHAR(50)
            );
        """)

        print("Tables and migrations applied successfully.")
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error migrating: {e}")

if __name__ == "__main__":
    migrate()
