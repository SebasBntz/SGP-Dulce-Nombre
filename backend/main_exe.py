import uvicorn
import os
import sys
import shutil
from datetime import datetime
from app.main import app
from app.core.config import settings
from app.db.session import engine
from app.models.all_models import Base

def perform_silent_backup():
    """Realiza una copia de seguridad automática al iniciar en una carpeta interna."""
    try:
        base_dir = settings.BASE_DATA_DIR
        db_path = os.path.join(base_dir, "parroquia.db")
        
        if not os.path.exists(db_path):
            return

        backup_dir = os.path.join(base_dir, "respaldos_automaticos")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Solo guardamos los últimos 5 respaldos automáticos para ahorrar espacio
        backups = sorted([os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith('.db')])
        if len(backups) >= 5:
            os.remove(backups[0])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"auto_respaldo_{timestamp}.db")
        
        shutil.copy2(db_path, backup_path)
        print(f"Respaldo automático creado: {backup_path}")
    except Exception as e:
        print(f"Error en respaldo automático: {e}")

def create_default_admin():
    """Crea el usuario admin por defecto si no existe ningún usuario."""
    from sqlalchemy.orm import Session
    from app.db.session import SessionLocal
    from app.models.all_models import Usuario, UsuarioRol
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        user_count = db.query(Usuario).count()
        if user_count == 0:
            admin = Usuario(
                email="admin@parroquia.com",
                password_hash=get_password_hash("admin123456"),
                nombre_completo="Administrador Parroquial",
                rol=UsuarioRol.ADMIN,
                is_active=True,
                activo=True,
                usuario="admin"
            )
            db.add(admin)
            db.commit()
            print("Usuario administrador creado automáticamente.")
        else:
            print(f"Base de datos OK: {user_count} usuario(s) encontrado(s).")
    except Exception as e:
        print(f"Error creando admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # 1. Crear tablas si no existen
    Base.metadata.create_all(bind=engine)

    # 2. Crear admin por defecto si la BD está vacía
    create_default_admin()
    
    # 3. Realizar respaldo silencioso al inicio
    if getattr(sys, 'frozen', False):
        perform_silent_backup()
    
    # 4. Lanzar servidor
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
