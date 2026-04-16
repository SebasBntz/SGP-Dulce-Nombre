from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

# --- Perfiles ---
class PerfilBase(BaseModel):
    nombre_perfil: str

class PerfilCreate(PerfilBase):
    pass

class Perfil(PerfilBase):
    id_perfil: int
    class Config:
        from_attributes = True

# --- Personas ---
class PersonaBase(BaseModel):
    nombres: str
    apellidos: str
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None

class PersonaCreate(PersonaBase):
    pass

class Persona(PersonaBase):
    id_persona: int
    fecha_registro: datetime
    class Config:
        from_attributes = True

# --- Sacerdotes ---
class SacerdoteBase(BaseModel):
    nombres: str
    apellidos: str
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None

class SacerdoteCreate(SacerdoteBase):
    pass

class Sacerdote(SacerdoteBase):
    id_sacerdote: int
    class Config:
        from_attributes = True

# --- Tipos de Sacramento ---
class TipoSacramentoBase(BaseModel):
    nombre: str

class TipoSacramentoCreate(TipoSacramentoBase):
    pass

class TipoSacramento(TipoSacramentoBase):
    id_tipo: int
    class Config:
        from_attributes = True

# --- Grupos ---
class GrupoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class GrupoCreate(GrupoBase):
    pass

class Grupo(GrupoBase):
    id_grupo: int
    class Config:
        from_attributes = True

class GrupoPersonaCreate(BaseModel):
    nombre_completo: str

class GrupoPersona(BaseModel):
    id_grupo: int
    id_persona: int
    fecha_ingreso: date
    class Config:
        from_attributes = True

# --- Aportes ---
class AporteBase(BaseModel):
    id_persona: Optional[int] = None
    monto: Decimal
    fecha: Optional[date] = None
    tipo: Optional[str] = None
    descripcion: Optional[str] = None

class AporteCreate(AporteBase):
    persona_nombre: Optional[str] = None

class Aporte(AporteBase):
    id_aporte: int
    persona_nombre: Optional[str] = None
    class Config:
        from_attributes = True
