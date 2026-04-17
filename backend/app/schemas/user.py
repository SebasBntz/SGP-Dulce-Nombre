from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UsuarioBase(BaseModel):
    email: EmailStr
    nombre_completo: str
    rol: str = "secretaria"

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    rol: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    usuario_id: int
    fecha_creacion: datetime
    
    model_config = ConfigDict(from_attributes=True)

# For compatibility with existing auth routes
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    token: str
    new_password: str

# Legacy names for easy refactoring
UserCreate = UsuarioCreate
UserResponse = UsuarioResponse
