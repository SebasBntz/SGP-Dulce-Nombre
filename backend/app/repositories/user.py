from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import CRUDBase
from app.models import Usuario
from app.schemas.user import UsuarioCreate, UsuarioUpdate
from app.core.security import get_password_hash

class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    """
    Repositorio para gestionar las operaciones de base de datos relacionadas con Usuarios (Parroquia).
    """
    def get_by_email(self, db: Session, *, email: str) -> Optional[Usuario]:
        """
        Busca un usuario por su email.
        """
        return db.query(Usuario).filter(Usuario.email == email).first()

    def create(self, db: Session, *, obj_in: UsuarioCreate) -> Usuario:
        """
        Crea un nuevo usuario con contraseña hasheada.
        """
        db_obj = Usuario(
            email=obj_in.email,
            password_hash=get_password_hash(obj_in.password),
            nombre_completo=obj_in.nombre_completo,
            rol=obj_in.rol
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

# Instancia global del repositorio de usuarios
user = CRUDUsuario(Usuario)
