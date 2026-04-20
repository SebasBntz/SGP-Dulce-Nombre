from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Dict, Any, Optional
from app.db.session import get_db
from app.models.all_models import (
    Persona, Sacerdote, Grupo, Aporte, GrupoPersona, 
    ActaBautizo, ActaMatrimonio, ActaConfirmacion, ActaComunion
)
from app.schemas.parroquia import (
    PersonaCreate, Persona as PersonaSchema,
    SacerdoteCreate, Sacerdote as SacerdoteSchema,
    GrupoCreate, Grupo as GrupoSchema,
    AporteCreate, Aporte as AporteSchema,
    GrupoPersonaCreate, GrupoPersona as GrupoPersonaSchema
)
from app.core.config import settings
import shutil
import os
from datetime import datetime

router = APIRouter()

# --- Dashboard Stats ---
@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    tot_bautizos = db.query(func.count(ActaBautizo.id)).scalar() or 0
    tot_matrimonios = db.query(func.count(ActaMatrimonio.id)).scalar() or 0
    tot_confirmaciones = db.query(func.count(ActaConfirmacion.id)).scalar() or 0
    tot_comuniones = db.query(func.count(ActaComunion.id)).scalar() or 0
    tot_aportes = db.query(func.sum(Aporte.monto)).scalar() or 0.0
    
    return {
        "bautizos": tot_bautizos,
        "matrimonios": tot_matrimonios,
        "confirmaciones": tot_confirmaciones,
        "comuniones": tot_comuniones,
        "aportes": float(tot_aportes)
    }

@router.get("/search/global")
def global_search(q: str, db: Session = Depends(get_db)):
    pattern = f"%{q}%"
    
    # Counts
    p_count = db.query(func.count(Persona.id_persona)).filter((Persona.nombres.ilike(pattern)) | (Persona.apellidos.ilike(pattern))).scalar()
    b_count = db.query(func.count(ActaBautizo.id)).filter((ActaBautizo.nombre.ilike(pattern)) | (ActaBautizo.apellidos.ilike(pattern))).scalar()
    m_count = db.query(func.count(ActaMatrimonio.id)).filter(
        (ActaMatrimonio.nombre_esposo.ilike(pattern)) | (ActaMatrimonio.apellidos_esposo.ilike(pattern)) |
        (ActaMatrimonio.nombre_esposa.ilike(pattern)) | (ActaMatrimonio.apellidos_esposa.ilike(pattern))
    ).scalar()
    conf_count = db.query(func.count(ActaConfirmacion.id)).filter((ActaConfirmacion.nombre.ilike(pattern)) | (ActaConfirmacion.apellidos.ilike(pattern))).scalar()
    com_count = db.query(func.count(ActaComunion.id)).filter((ActaComunion.nombre.ilike(pattern)) | (ActaComunion.apellidos.ilike(pattern))).scalar()
    
    # For Groups and Aportes, we relate to personas
    persona_ids = db.query(Persona.id_persona).filter((Persona.nombres.ilike(pattern)) | (Persona.apellidos.ilike(pattern))).all()
    p_ids = [p[0] for p in persona_ids]
    
    g_count = db.query(func.count(GrupoPersona.id_persona)).filter(GrupoPersona.id_persona.in_(p_ids)).scalar() if p_ids else 0
    a_count = db.query(func.count(Aporte.id_aporte)).filter(Aporte.id_persona.in_(p_ids)).scalar() if p_ids else 0

    return {
        "query": q,
        "personas": p_count,
        "bautizos": b_count,
        "matrimonios": m_count,
        "confirmaciones": conf_count,
        "comuniones": com_count,
        "grupos": g_count,
        "aportes": a_count
    }



# --- Personas ---
@router.get("/personas/", response_model=Any)
def read_personas(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None)
):
    query = db.query(Persona)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(or_(Persona.nombres.ilike(search_filter), Persona.apellidos.ilike(search_filter)))
    
    total = query.count()
    records = query.offset(skip).limit(limit).all()
    return {"records": jsonable_encoder(records), "total": total}

@router.post("/personas/", response_model=Any)
def create_persona(persona: PersonaCreate, db: Session = Depends(get_db)):
    db_persona = Persona(**persona.model_dump())
    db.add(db_persona)
    db.commit()
    db.refresh(db_persona)
    return db_persona

# --- Sacerdotes ---
@router.get("/sacerdotes/", response_model=Any)
def read_sacerdotes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    total = db.query(Sacerdote).count()
    records = db.query(Sacerdote).offset(skip).limit(limit).all()
    return {"records": jsonable_encoder(records), "total": total}

@router.post("/sacerdotes/", response_model=SacerdoteSchema)
def create_sacerdote(sacerdote: SacerdoteCreate, db: Session = Depends(get_db)):
    db_sacerdote = Sacerdote(**sacerdote.model_dump())
    db.add(db_sacerdote)
    db.commit()
    db.refresh(db_sacerdote)
    return db_sacerdote

# --- Grupos ---
@router.get("/grupos/", response_model=Any)
def read_grupos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    total = db.query(Grupo).count()
    records = db.query(Grupo).offset(skip).limit(limit).all()
    return {"records": jsonable_encoder(records), "total": total}

@router.post("/grupos/", response_model=GrupoSchema)
def create_grupo(grupo: GrupoCreate, db: Session = Depends(get_db)):
    db_grupo = Grupo(**grupo.model_dump())
    db.add(db_grupo)
    db.commit()
    db.refresh(db_grupo)
    return db_grupo

@router.get("/grupos/{id_grupo}/miembros", response_model=List[PersonaSchema])
def read_grupo_miembros(id_grupo: int, db: Session = Depends(get_db)):
    grupo = db.query(Grupo).filter(Grupo.id_grupo == id_grupo).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    miembros = db.query(Persona).join(GrupoPersona).filter(GrupoPersona.id_grupo == id_grupo).all()
    return miembros

def find_or_create_persona(nombre_completo: str, db: Session) -> Persona:
    # Separar primer nombre y apellido (muy básico)
    parts = nombre_completo.strip().split(' ', 1)
    nombres = parts[0]
    apellidos = parts[1] if len(parts) > 1 else ""
    
    # Buscar existente
    persona = db.query(Persona).filter(
        Persona.nombres.ilike(nombres),
        Persona.apellidos.ilike(apellidos)
    ).first()
    
    if not persona:
        persona = Persona(nombres=nombres, apellidos=apellidos)
        db.add(persona)
        db.commit()
        db.refresh(persona)
    
    return persona

@router.post("/grupos/{id_grupo}/miembros", response_model=GrupoPersonaSchema)
def add_persona_to_grupo(id_grupo: int, gp: GrupoPersonaCreate, db: Session = Depends(get_db)):
    # Verify group exists
    grupo = db.query(Grupo).filter(Grupo.id_grupo == id_grupo).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    # Find or create persona by name
    persona = find_or_create_persona(gp.nombre_completo, db)

    # Check if already a member
    existente = db.query(GrupoPersona).filter(
        GrupoPersona.id_grupo == id_grupo,
        GrupoPersona.id_persona == persona.id_persona
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="La persona ya pertenece al grupo")

    # Add member
    nuevo_miembro = GrupoPersona(id_grupo=id_grupo, id_persona=persona.id_persona)
    db.add(nuevo_miembro)
    db.commit()
    db.refresh(nuevo_miembro)
    return nuevo_miembro

# --- Aportes ---
@router.get("/aportes/balance", response_model=Dict[str, Any])
def get_aportes_balance(db: Session = Depends(get_db)):
    # Totales por mes
    resultados_mes = (
        db.query(
            func.strftime('%Y-%m', Aporte.fecha).label('mes'),
            func.sum(Aporte.monto).label('total')
        )
        .group_by(func.strftime('%Y-%m', Aporte.fecha))
        .order_by(func.strftime('%Y-%m', Aporte.fecha).asc()) # Ascendente para el gráfico
        .all()
    )
    
    # Desglose por tipo
    desglose_tipo = (
        db.query(
            Aporte.tipo,
            func.sum(Aporte.monto).label('total')
        )
        .group_by(Aporte.tipo)
        .all()
    )
    
    # Estadísticas rápidas
    total_historico = db.query(func.sum(Aporte.monto)).scalar() or 0.0
    promedio_mensual = 0.0
    if resultados_mes:
        promedio_mensual = total_historico / len(resultados_mes)
    
    return {
        "mensual": [{"mes": r.mes if r.mes else "S/F", "total": float(r.total)} for r in resultados_mes],
        "por_tipo": [{"tipo": r.tipo, "total": float(r.total)} for r in desglose_tipo],
        "stats": {
            "total_historico": float(total_historico),
            "promedio_mensual": float(promedio_mensual),
            "conteo_meses": len(resultados_mes)
        }
    }

@router.get("/aportes/", response_model=Any)
def read_aportes(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None)
):
    query = db.query(
        Aporte.id_aporte,
        Aporte.monto,
        Aporte.fecha,
        Aporte.tipo,
        Aporte.descripcion,
        (Persona.nombres + ' ' + Persona.apellidos).label('persona_nombre')
    ).outerjoin(Persona, Aporte.id_persona == Persona.id_persona)
    
    if search:
        sf = f"%{search}%"
        query = query.filter(or_(
            Persona.nombres.ilike(sf), 
            Persona.apellidos.ilike(sf),
            Aporte.tipo.ilike(sf)
        ))
    
    total = query.count()
    results = query.offset(skip).limit(limit).all()
    # Convert results to a list of dicts with mapped keys
    records_list = [dict(row._mapping) for row in results]
    return {"records": jsonable_encoder(records_list), "total": total}

@router.post("/aportes/", response_model=Any)
def create_aporte(aporte: AporteCreate, db: Session = Depends(get_db)):
    # Si viene con nombre, buscar/crear persona
    data = aporte.model_dump()
    if data.get("persona_nombre"):
        persona = find_or_create_persona(data.pop("persona_nombre"), db)
        data["id_persona"] = persona.id_persona
        
    db_aporte = Aporte(**data)
    db.add(db_aporte)
    db.commit()
    db.refresh(db_aporte)
    return jsonable_encoder(db_aporte)

# --- Database Backup ---
@router.post("/db/backup")
def create_backup(destination_dir: str):
    """
    Copia el archivo de la base de datos SQLite a la ruta especificada.
    """
    try:
        # Obtener ruta absoluta del archivo .db quitando 'sqlite:///'
        db_uri = settings.SQLALCHEMY_DATABASE_URI
        if db_uri.startswith("sqlite:///"):
            db_path = db_uri.replace("sqlite:///", "")
        else:
            raise HTTPException(status_code=400, detail="Solo se permiten respaldos de SQLite")

        if not os.path.exists(db_path):
            raise HTTPException(status_code=404, detail="Archivo de base de datos no encontrado")

        if not os.path.isdir(destination_dir):
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
            else:
                raise HTTPException(status_code=400, detail="La ruta de destino no es un directorio")

        # Crear nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"respaldo_parroquia_{timestamp}.db"
        dest_path = os.path.join(destination_dir, backup_filename)

        shutil.copy2(db_path, dest_path)
        return {"status": "ok", "message": f"Respaldo creado en {dest_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
