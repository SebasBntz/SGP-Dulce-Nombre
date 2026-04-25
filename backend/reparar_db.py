import sqlite3
import os
from pathlib import Path

def fix_database():
    # Ruta a la base de datos en Documentos
    db_path = os.path.join(os.path.expanduser("~"), "Documents", "Datos Parroquia", "parroquia.db")
    
    if not os.path.exists(db_path):
        print(f"No se encontró la base de datos en: {db_path}")
        return

    print(f"Reparando base de datos en: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Reparar grupo_persona (añadir fecha_ingreso)
        cursor.execute("PRAGMA table_info(grupo_persona)")
        columns = [row[1] for row in cursor.fetchall()]
        if "fecha_ingreso" not in columns:
            print("Añadiendo columna 'fecha_ingreso' a 'grupo_persona'...")
            cursor.execute("ALTER TABLE grupo_persona ADD COLUMN fecha_ingreso DATE DEFAULT CURRENT_DATE")
        
        # 2. Reparar aportes (añadir descripcion si falta)
        cursor.execute("PRAGMA table_info(aportes)")
        columns = [row[1] for row in cursor.fetchall()]
        if "descripcion" not in columns:
            print("Añadiendo columna 'descripcion' a 'aportes'...")
            cursor.execute("ALTER TABLE aportes ADD COLUMN descripcion TEXT")

        conn.commit()
        print("\n¡Base de datos reparada con éxito!")
    except Exception as e:
        print(f"\nError al reparar: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()
