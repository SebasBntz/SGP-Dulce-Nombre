from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base

class UsuarioRol(str, enum.Enum):
    CURA = "cura"
    SECRETARIA = "secretaria"
    ADMIN = "admin"

class PasswordResetPin(Base):
    __tablename__ = "password_resets"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    pin = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

class Perfil(Base):
    __tablename__ = "perfiles"
    id_perfil = Column(Integer, primary_key=True, index=True)
    nombre_perfil = Column(String(100), nullable=False)
    
    usuarios = relationship("Usuario", back_populates="perfil_rel")

class Usuario(Base):
    __tablename__ = "usuarios"
    usuario_id = Column(Integer, primary_key=True) # Mantener compatible con login actual si es posible
    nombre_completo = Column(String(255), nullable=True) # Opcional según diagrama
    email = Column(String(255), unique=True, index=True, nullable=True) # Opcional según diagrama
    usuario = Column(String(50), unique=True, index=True) # Según diagrama 'Usuario'
    clave = Column(String(255)) # Según diagrama 'Clave'
    password_hash = Column(String(255)) # Mantener para compatibilidad
    id_perfil = Column(Integer, ForeignKey("perfiles.id_perfil"), nullable=True)
    rol = Column(String(50), default=UsuarioRol.SECRETARIA) # Mantener para compatibilidad
    activo = Column(Boolean(), default=True) # Según diagrama 'Activo'
    is_active = Column(Boolean(), default=True) # Mantener para compatibilidad
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    
    perfil_rel = relationship("Perfil", back_populates="usuarios")

class Persona(Base):
    __tablename__ = "personas"
    id_persona = Column(Integer, primary_key=True)
    nombres = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)
    fecha_nacimiento = Column(Date)
    direccion = Column(String(255))
    telefono = Column(String(50))
    email = Column(String(255))
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    
    sacramentos = relationship("Sacramento", back_populates="persona")
    aportes = relationship("Aporte", back_populates="persona")
    grupos_vinculados = relationship("GrupoPersona", back_populates="persona")
    grupo_aportes = relationship("GrupoAporte", back_populates="persona")

class Sacerdote(Base):
    __tablename__ = "sacerdotes"
    id_sacerdote = Column(Integer, primary_key=True)
    nombres = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)
    telefono = Column(String(50))
    email = Column(String(255))
    
    sacramentos = relationship("Sacramento", back_populates="sacerdote")

class TipoSacramento(Base):
    __tablename__ = "tipos_sacramento"
    id_tipo = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    
    sacramentos = relationship("Sacramento", back_populates="tipo_sacramento")

class Sacramento(Base):
    __tablename__ = "sacramentos"
    id_sacramento = Column(Integer, primary_key=True)
    id_persona = Column(Integer, ForeignKey("personas.id_persona"))
    id_tipo = Column(Integer, ForeignKey("tipos_sacramento.id_tipo"))
    id_sacerdote = Column(Integer, ForeignKey("sacerdotes.id_sacerdote"))
    fecha = Column(Date)
    observaciones = Column(Text)
    
    persona = relationship("Persona", back_populates="sacramentos")
    tipo_sacramento = relationship("TipoSacramento", back_populates="sacramentos")
    sacerdote = relationship("Sacerdote", back_populates="sacramentos")

class Grupo(Base):
    __tablename__ = "grupos"
    id_grupo = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    
    miembros = relationship("GrupoPersona", back_populates="grupo")
    aportes = relationship("GrupoAporte", back_populates="grupo")

class GrupoPersona(Base):
    __tablename__ = "grupo_persona"
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo"), primary_key=True)
    id_persona = Column(Integer, ForeignKey("personas.id_persona"), primary_key=True)
    fecha_ingreso = Column(Date, server_default=func.current_date())
    
    grupo = relationship("Grupo", back_populates="miembros")
    persona = relationship("Persona", back_populates="grupos_vinculados")

class GrupoAporte(Base):
    __tablename__ = "grupo_aportes"
    id_grupo_aporte = Column(Integer, primary_key=True)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo"))
    id_persona = Column(Integer, ForeignKey("personas.id_persona"))
    monto = Column(Numeric(12, 2))
    fecha = Column(Date)
    tipo = Column(String(50))
    
    grupo = relationship("Grupo", back_populates="aportes")
    persona = relationship("Persona", back_populates="grupo_aportes")

class Aporte(Base):
    __tablename__ = "aportes"
    id_aporte = Column(Integer, primary_key=True)
    id_persona = Column(Integer, ForeignKey("personas.id_persona"), nullable=True)
    monto = Column(Numeric(12, 2))
    fecha = Column(Date)
    tipo = Column(String(50))
    descripcion = Column(Text)
    
    persona = relationship("Persona", back_populates="aportes")

# --- Tablas de Actas (Se mantienen igual según requerimiento) ---

class ActaBautizo(Base):
    __tablename__ = "actas_bautizo"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)
    fecha_nacimiento = Column(Date)
    lugar_nacimiento = Column(String(255))
    fecha_bautizo = Column(Date, nullable=False)
    nombre_padre = Column(String(255))
    nombre_madre = Column(String(255))
    nombre_padrino = Column(String(255))
    nombre_madrina = Column(String(255))
    nombre_abuelo_paterno = Column(String(255))
    nombre_abuela_paterna = Column(String(255))
    nombre_abuelo_materno = Column(String(255))
    nombre_abuela_materna = Column(String(255))
    abuelos_paternos = Column(Text)
    abuelos_maternos = Column(Text)
    nombre_cura = Column(String(255))
    da_fe = Column(String(255))
    nota_al_margen = Column(Text)
    libro = Column(String(50))
    folio = Column(String(50))
    numero = Column(String(50))
    archivo_adjunto = Column(String(255))
    parroco_firmante = Column(String(255))
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

class ActaMatrimonio(Base):
    __tablename__ = "actas_matrimonio"
    id = Column(Integer, primary_key=True)
    nombre_esposo = Column(String(255), nullable=False)
    apellidos_esposo = Column(String(255), nullable=False)
    padres_esposo = Column(String(255))
    parroquia_bautizo_esposo = Column(String(255))
    fecha_bautizo_esposo = Column(Date)
    
    nombre_esposa = Column(String(255), nullable=False)
    apellidos_esposa = Column(String(255), nullable=False)
    padres_esposa = Column(String(255))
    parroquia_bautizo_esposa = Column(String(255))
    fecha_bautizo_esposa = Column(Date)

    fecha_matrimonio = Column(Date, nullable=False)
    lugar_celebracion = Column(String(255), default="Parroquia")
    nombre_padrino = Column(String(255))
    nombre_madrina = Column(String(255))
    nombre_testigo1 = Column(String(255))
    nombre_testigo2 = Column(String(255))
    testigos = Column(Text)
    nombre_cura = Column(String(255))
    legitimacion_hijos = Column(Text)
    da_fe = Column(String(255))
    nota_al_margen = Column(Text)
    
    libro = Column(String(50))
    folio = Column(String(50))
    numero = Column(String(50))
    archivo_adjunto = Column(String(255))
    parroco_firmante = Column(String(255))
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

class ActaConfirmacion(Base):
    __tablename__ = "actas_confirmacion"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)
    fecha_nacimiento = Column(Date)
    fecha_bautizo = Column(Date)
    parroquia_bautizo = Column(String(255))
    lugar_confirmacion = Column(String(255))
    lugar_bautismo = Column(String(255))
    fecha_confirmacion = Column(Date, nullable=False)
    nombre_padre = Column(String(255))
    nombre_madre = Column(String(255))
    nombre_padrino = Column(String(255))
    nombre_madrina = Column(String(255))
    nombre_cura = Column(String(255))
    obispo = Column(String(255))
    da_fe = Column(String(255))
    nota_al_margen = Column(Text)
    libro = Column(String(50))
    folio = Column(String(50))
    numero = Column(String(50))
    archivo_adjunto = Column(String(255))
    parroco_firmante = Column(String(255))
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

class ActaComunion(Base):
    __tablename__ = "actas_comunion"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)
    fecha_nacimiento = Column(Date)
    fecha_bautizo = Column(Date)
    parroquia_bautizo = Column(String(255))
    lugar_comunion = Column(String(255))
    lugar_bautismo = Column(String(255))
    fecha_comunion = Column(Date, nullable=False)
    nombre_padre = Column(String(255))
    nombre_madre = Column(String(255))
    padrino = Column(String(255))
    madrina = Column(String(255))
    nombre_cura = Column(String(255))
    da_fe = Column(String(255))
    nota_al_margen = Column(Text)
    libro = Column(String(50))
    folio = Column(String(50))
    numero = Column(String(50))
    archivo_adjunto = Column(String(255))
    parroco_firmante = Column(String(255))
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

