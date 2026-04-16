from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Configuración del contexto de encriptación usando Argon2 para el hash de contraseñas
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Genera un token de acceso JWT firmado con la clave secreta del proyecto.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Por defecto usa la duración definida en la configuración (app/core/config.py)
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict | None:
    """
    Decodifica y verifica la autenticidad de un token JWT. 
    Retorna los datos contenidos (payload) o None si el token es inválido o expiró.
    """
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_token
    except jwt.JWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compara una contraseña en texto plano con un hash almacenado para verificar si coinciden.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro para una contraseña antes de guardarla en la base de datos.
    """
    return pwd_context.hash(password)
