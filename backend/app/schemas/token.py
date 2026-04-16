from typing import Optional
from pydantic import BaseModel
from .user import UserResponse

# Esquema para el token de acceso JWT devuelto tras el inicio de sesión
class Token(BaseModel):
    access_token: str # Cadena JWT generada
    token_type: str # Ej: "bearer"

# Respuesta completa de autenticación exitosa (Token + Datos del usuario)
class AuthResponse(Token):
    user: UserResponse

# Datos decodificados provenientes de un token JWT válido
class TokenData(BaseModel):
    # El 'sub' habitualmente contiene el email o el ID del usuario
    id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
