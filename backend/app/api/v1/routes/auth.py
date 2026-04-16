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

    # Intento de envío de email de bienvenida
    try:
        email_service.send_welcome_email(user.email, user.nombre_completo)
    except Exception as e:
        print(f"Error enviando correo de bienvenida: {e}")

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
    Solicita un enlace de recuperación de contraseña.
    """
    try:
        user = user_repo.get_by_email(db, email=req.email)
        if not user:
            return {"message": "Si el usuario existe, se ha enviado un correo de recuperación."}

        reset_token_expires = timedelta(minutes=15)
        reset_token = security.create_access_token(
            {"sub": user.email, "type": "reset"},
            expires_delta=reset_token_expires,
        )

        email_service.send_password_reset_email(user.email, reset_token)

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
    Valida el token de recuperación y actualiza la contraseña del usuario.
    """
    try:
        payload = security.decode_token(req.token)
        if not payload or payload.get("type") != "reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de recuperación inválido o expirado",
            )

        email = payload.get("sub")
        user = user_repo.get_by_email(db, email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        user.password_hash = security.get_password_hash(req.new_password)
        db.add(user)
        db.commit()
        db.refresh(user)

        return {"message": "Contraseña actualizada con éxito"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en reset_password: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
