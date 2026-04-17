import os
import sys
from pathlib import Path

# Add backend to sys.path
backend_path = Path(__file__).resolve().parent
sys.path.append(str(backend_path))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.all_models import Usuario, UsuarioRol
from app.core.security import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin_email = "sebastianjey@gmail.com"
        existing_user = db.query(Usuario).filter(Usuario.email == admin_email).first()
        
        if existing_user:
            print(f"User {admin_email} already exists.")
            return

        # Create new admin
        new_admin = Usuario(
            email=admin_email,
            password_hash=get_password_hash("admin123456"),
            nombre_completo="Administrador Parroquial",
            rol=UsuarioRol.ADMIN,
            is_active=True,
            activo=True,
            usuario="admin_sebastian"
        )
        
        db.add(new_admin)
        db.commit()
        print(f"Admin user created successfully!")
        print(f"Email: {admin_email}")
        print(f"Password: admin123456")
        
    except Exception as e:
        print(f"Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
