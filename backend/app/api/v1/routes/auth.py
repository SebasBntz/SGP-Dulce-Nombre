from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.core import security
from app.core.config import settings
from app.schemas.token import AuthResponse
from app.schemas.user import UsuarioCreate, UsuarioResponse, ForgotPasswordRequest, ResetPassword
from app.repositories import user as user_repo
from app.services import email_service
from app.models.all_models import PasswordResetPin
import random
from datetime import datetime, timezone
class LoginRequest(BaseModel):
    """Esquema para capturar las credenciales de inicio de sesión."""
    email: EmailStr
    password: str


router = APIRouter()


@router.post("/login", response_model=AuthResponse)
def login_access_token(
    *, db: Session = Depends(get_db), credentials: LoginRequest
) -> Any:
    """
    Punto de entrada para la autenticación de usuarios de la Parroquia.
    Verifica credenciales y devuelve un token JWT si son válidas.
    """
    user = user_repo.get_by_email(db, email=credentials.email)
    if not user or not security.verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Correo electrónico o contraseña incorrectos",
        )

    # Generación del token de acceso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        {"sub": user.email, "id": user.usuario_id, "role": user.rol},
        expires_delta=access_token_expires,
    )
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UsuarioResponse.model_validate(user),
    )


@router.post("/register", response_model=AuthResponse)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UsuarioCreate,
) -> Any:
    """
    Registra un nuevo usuario de la Parroquia (Cura o Secretaria).
    """
    existing = user_repo.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un usuario con este correo electrónico en el sistema de la Parroquia",
        )

    user = user_repo.create(db, obj_in=user_in)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        {"sub": user.email, "id": user.usuario_id, "role": user.rol},
        expires_delta=access_token_expires,
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UsuarioResponse.model_validate(user),
    )


@router.post("/forgot-password")
def forgot_password(
    *,
    db: Session = Depends(get_db),
    req: ForgotPasswordRequest
) -> Any:
    """
    Solicita un PIN de recuperación de contraseña de 6 dígitos.
    """
    try:
        user = user_repo.get_by_email(db, email=req.email)
        if not user:
            return {"message": "Si el usuario existe, se ha enviado un correo de recuperación."}

        pin = f"{random.randint(100000, 999999)}"
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        # Eliminar PINs anteriores del mismo correo
        db.query(PasswordResetPin).filter(PasswordResetPin.email == user.email).delete()
        
        reset_entry = PasswordResetPin(email=user.email, pin=pin, expires_at=expires)
        db.add(reset_entry)
        db.commit()

        email_service.send_password_reset_email(user.email, pin)

        return {"message": "Si el usuario existe, se ha enviado un correo de recuperación."}
    except Exception as e:
        print(f"Error en forgot_password: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/reset-password")
def reset_password(
    *,
    db: Session = Depends(get_db),
    req: ResetPassword
) -> Any:
    """
    Valida el PIN de recuperación y actualiza la contraseña del usuario.
    """
    try:
        pin_entry = db.query(PasswordResetPin).filter(
            PasswordResetPin.email == req.email,
            PasswordResetPin.pin == req.token
        ).first()

        # Evitar comparar fechas naive con aware, convertir expires_at a aware si es naive
        # o comparar si expiro:
        if not pin_entry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PIN inválido",
            )
            
        current_time = datetime.now(timezone.utc)
        if pin_entry.expires_at.tzinfo is None:
             current_time = datetime.utcnow()
             
        if pin_entry.expires_at < current_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El PIN ha expirado",
            )

        user = user_repo.get_by_email(db, email=req.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        user.password_hash = security.get_password_hash(req.new_password)
        db.query(PasswordResetPin).filter(PasswordResetPin.email == req.email).delete()
        
        db.add(user)
        db.commit()
        db.refresh(user)

        return {"message": "Contraseña actualizada con éxito"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en reset_password: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
