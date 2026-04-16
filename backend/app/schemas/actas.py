from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr

# Base Schema
class ActaBase(BaseModel):
    nombre: str
    apellidos: str
    fecha_nacimiento: Optional[date] = None
    fecha_registro: Optional[datetime] = None
    libro: Optional[str] = None
    folio: Optional[str] = None
    numero: Optional[str] = None
    archivo_adjunto: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# 1. Bautizo
class ActaBautizoBase(ActaBase):
    lugar_nacimiento: Optional[str] = None
    fecha_bautizo: date
    nombre_padre: Optional[str] = None
    nombre_madre: Optional[str] = None
    nombre_padrino: Optional[str] = None
    nombre_madrina: Optional[str] = None
    nombre_abuelo_paterno: Optional[str] = None
    nombre_abuela_paterna: Optional[str] = None
    nombre_abuelo_materno: Optional[str] = None
    nombre_abuela_materna: Optional[str] = None
    abuelos_paternos: Optional[str] = None
    abuelos_maternos: Optional[str] = None
    nombre_cura: Optional[str] = None
    da_fe: Optional[str] = None
    nota_al_margen: Optional[str] = None

class ActaBautizoCreate(ActaBautizoBase):
    pass

class ActaBautizo(ActaBautizoBase):
    id: int

# 2. Matrimonio
class ActaMatrimonioBase(BaseModel):
    nombre_esposo: str
    apellidos_esposo: Optional[str] = ""
    padres_esposo: Optional[str] = None
    parroquia_bautizo_esposo: Optional[str] = None
    fecha_bautizo_esposo: Optional[date] = None

    nombre_esposa: str
    apellidos_esposa: Optional[str] = ""
    padres_esposa: Optional[str] = None
    parroquia_bautizo_esposa: Optional[str] = None
    fecha_bautizo_esposa: Optional[date] = None

    fecha_matrimonio: date
    lugar_celebracion: Optional[str] = "Parroquia"
    nombre_padrino: Optional[str] = None
    nombre_madrina: Optional[str] = None
    nombre_testigo1: Optional[str] = None
    nombre_testigo2: Optional[str] = None
    nombre_cura: Optional[str] = None
    legitimacion_hijos: Optional[str] = None
    testigos: Optional[str] = None
    da_fe: Optional[str] = None
    nota_al_margen: Optional[str] = None

    libro: Optional[str] = None
    folio: Optional[str] = None
    numero: Optional[str] = None
    archivo_adjunto: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ActaMatrimonioCreate(ActaMatrimonioBase):
    pass

class ActaMatrimonio(ActaMatrimonioBase):
    id: int

# 3. Confirmación
class ActaConfirmacionBase(ActaBase):
    fecha_bautizo: Optional[date] = None
    parroquia_bautizo: Optional[str] = None
    lugar_confirmacion: Optional[str] = None
    lugar_bautismo: Optional[str] = None
    fecha_confirmacion: date
    nombre_padre: Optional[str] = None
    nombre_madre: Optional[str] = None
    nombre_padrino: Optional[str] = None
    nombre_madrina: Optional[str] = None
    nombre_cura: Optional[str] = None
    obispo: Optional[str] = None
    da_fe: Optional[str] = None
    nota_al_margen: Optional[str] = None

class ActaConfirmacionCreate(ActaConfirmacionBase):
    pass

class ActaConfirmacion(ActaConfirmacionBase):
    id: int

# 4. Primera Comunión
class ActaComunionBase(ActaBase):
    fecha_bautizo: Optional[date] = None
    parroquia_bautizo: Optional[str] = None
    lugar_comunion: Optional[str] = None
    lugar_bautismo: Optional[str] = None
    fecha_comunion: date
    nombre_padre: Optional[str] = None
    nombre_madre: Optional[str] = None
    padrino: Optional[str] = None
    madrina: Optional[str] = None
    nombre_cura: Optional[str] = None
    da_fe: Optional[str] = None
    nota_al_margen: Optional[str] = None

class ActaComunionCreate(ActaComunionBase):
    pass

class ActaComunion(ActaComunionBase):
    id: int

# 5. Usuario (Simplified)
class UsuarioBase(BaseModel):
    nombre_completo: str
    email: EmailStr
    rol: str = "secretaria"

class UsuarioCreate(UsuarioBase):
    password: str

class Usuario(UsuarioBase):
    usuario_id: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)
