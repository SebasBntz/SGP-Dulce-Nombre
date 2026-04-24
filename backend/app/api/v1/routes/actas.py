from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models import all_models as models
from app.schemas import actas as schemas
from app.services.pdf_service import pdf_service

router = APIRouter()

# --- Bautizos ---
@router.post("/bautizos/", response_model=schemas.ActaBautizo)
def create_bautizo(
    *,
    db: Session = Depends(get_db),
    acta_in: schemas.ActaBautizoCreate
) -> Any:
    """Registrar un acta de bautizo"""
    obj = models.ActaBautizo(**acta_in.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/bautizos/", response_model=Any)
def read_bautizos(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None)
) -> Any:
    """Consultar actas de bautizo con búsqueda global"""
    query = db.query(models.ActaBautizo)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                models.ActaBautizo.nombre.ilike(search_filter),
                models.ActaBautizo.apellidos.ilike(search_filter),
                models.ActaBautizo.libro.ilike(search_filter),
                models.ActaBautizo.folio.ilike(search_filter),
                models.ActaBautizo.numero.ilike(search_filter)
            )
        )
    
    total = query.count()
    records = query.offset(skip).limit(limit).all()
    return {"records": jsonable_encoder(records), "total": total}

@router.get("/bautizos/{id}/pdf")
def get_bautizo_pdf(id: int, db: Session = Depends(get_db)):
    acta = db.query(models.ActaBautizo).filter(models.ActaBautizo.id == id).first()
    if not acta:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    
    pdf_content = pdf_service.generate_bautizo_pdf(acta)
    filename = f"partida_bautismo_{acta.nombre}_{acta.apellidos}.pdf".replace(" ", "_").upper()
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.put("/bautizos/{id}", response_model=schemas.ActaBautizo)
def update_bautizo(
    *,
    db: Session = Depends(get_db),
    id: int,
    acta_in: schemas.ActaBautizoCreate
) -> Any:
    """Actualizar un acta de bautizo"""
    obj = db.query(models.ActaBautizo).filter(models.ActaBautizo.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    
    update_data = acta_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)
    
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/bautizos/{id}")
def delete_bautizo(id: int, db: Session = Depends(get_db)):
    obj = db.query(models.ActaBautizo).filter(models.ActaBautizo.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    db.delete(obj)
    db.commit()
    return {"status": "ok"}

# --- Matrimonios ---
@router.post("/matrimonios/", response_model=schemas.ActaMatrimonio)
def create_matrimonio(
    *,
    db: Session = Depends(get_db),
    acta_in: schemas.ActaMatrimonioCreate
) -> Any:
    """Registrar un acta de matrimonio"""
    obj = models.ActaMatrimonio(**acta_in.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/matrimonios/", response_model=Any)
def read_matrimonios(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None)
) -> Any:
    """Consultar actas de matrimonio con búsqueda global"""
    query = db.query(models.ActaMatrimonio)
    if search:
        sf = f"%{search}%"
        query = query.filter(
            or_(
                models.ActaMatrimonio.nombre_esposo.ilike(sf),
                models.ActaMatrimonio.apellidos_esposo.ilike(sf),
                models.ActaMatrimonio.nombre_esposa.ilike(sf),
                models.ActaMatrimonio.apellidos_esposa.ilike(sf),
                models.ActaMatrimonio.libro.ilike(sf),
                models.ActaMatrimonio.folio.ilike(sf),
                models.ActaMatrimonio.numero.ilike(sf)
            )
        )
    
    total = query.count()
    records = query.offset(skip).limit(limit).all()
    return {"records": jsonable_encoder(records), "total": total}

@router.get("/matrimonios/{id}/pdf")
def get_matrimonio_pdf(id: int, db: Session = Depends(get_db)):
    acta = db.query(models.ActaMatrimonio).filter(models.ActaMatrimonio.id == id).first()
    if not acta:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    
    pdf_content = pdf_service.generate_matrimonio_pdf(acta)
    filename = f"partida_matrimonio_{acta.nombre_esposo}_y_{acta.nombre_esposa}.pdf".replace(" ", "_").upper()
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.put("/matrimonios/{id}", response_model=schemas.ActaMatrimonio)
def update_matrimonio(
    *,
    db: Session = Depends(get_db),
    id: int,
    acta_in: schemas.ActaMatrimonioCreate
) -> Any:
    """Actualizar un acta de matrimonio"""
    obj = db.query(models.ActaMatrimonio).filter(models.ActaMatrimonio.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    
    update_data = acta_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)
    
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/matrimonios/{id}")
def delete_matrimonio(id: int, db: Session = Depends(get_db)):
    obj = db.query(models.ActaMatrimonio).filter(models.ActaMatrimonio.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    db.delete(obj)
    db.commit()
    return {"status": "ok"}

# --- Confirmaciones ---
@router.post("/confirmaciones/", response_model=schemas.ActaConfirmacion)
def create_confirmacion(
    *,
    db: Session = Depends(get_db),
    acta_in: schemas.ActaConfirmacionCreate
) -> Any:
    """Registrar un acta de confirmación"""
    obj = models.ActaConfirmacion(**acta_in.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/confirmaciones/", response_model=Any)
def read_confirmaciones(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None)
) -> Any:
    """Consultar actas de confirmación con búsqueda global"""
    query = db.query(models.ActaConfirmacion)
    if search:
        sf = f"%{search}%"
        query = query.filter(
            or_(
                models.ActaConfirmacion.nombre.ilike(sf),
                models.ActaConfirmacion.apellidos.ilike(sf),
                models.ActaConfirmacion.libro.ilike(sf),
                models.ActaConfirmacion.folio.ilike(sf),
                models.ActaConfirmacion.numero.ilike(sf)
            )
        )
    total = query.count()
    records = query.offset(skip).limit(limit).all()
    return {"records": jsonable_encoder(records), "total": total}

@router.get("/confirmaciones/{id}/pdf")
def get_confirmacion_pdf(id: int, db: Session = Depends(get_db)):
    acta = db.query(models.ActaConfirmacion).filter(models.ActaConfirmacion.id == id).first()
    if not acta:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    
    pdf_content = pdf_service.generate_confirmacion_pdf(acta)
    filename = f"partida_confirmacion_{acta.nombre}_{acta.apellidos}.pdf".replace(" ", "_").upper()
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.put("/confirmaciones/{id}", response_model=schemas.ActaConfirmacion)
def update_confirmacion(
    *,
    db: Session = Depends(get_db),
    id: int,
    acta_in: schemas.ActaConfirmacionCreate
) -> Any:
    """Actualizar un acta de confirmación"""
    obj = db.query(models.ActaConfirmacion).filter(models.ActaConfirmacion.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    
    update_data = acta_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)
    
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/confirmaciones/{id}")
def delete_confirmacion(id: int, db: Session = Depends(get_db)):
    obj = db.query(models.ActaConfirmacion).filter(models.ActaConfirmacion.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    db.delete(obj)
    db.commit()
    return {"status": "ok"}

# --- Comuniones ---
@router.post("/comuniones/", response_model=schemas.ActaComunion)
def create_comunion(
    *,
    db: Session = Depends(get_db),
    acta_in: schemas.ActaComunionCreate
) -> Any:
    """Registrar un acta de primera comunión"""
    obj = models.ActaComunion(**acta_in.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/comuniones/", response_model=Any)
def read_comuniones(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None)
) -> Any:
    """Consultar actas de primera comunión con búsqueda global"""
    query = db.query(models.ActaComunion)
    if search:
        sf = f"%{search}%"
        query = query.filter(
            or_(
                models.ActaComunion.nombre.ilike(sf),
                models.ActaComunion.apellidos.ilike(sf),
                models.ActaComunion.libro.ilike(sf),
                models.ActaComunion.folio.ilike(sf),
                models.ActaComunion.numero.ilike(sf)
            )
        )
    total = query.count()
    records = query.offset(skip).limit(limit).all()
    return {"records": jsonable_encoder(records), "total": total}

@router.get("/comuniones/{id}/pdf")
def get_comunion_pdf(id: int, db: Session = Depends(get_db)):
    acta = db.query(models.ActaComunion).filter(models.ActaComunion.id == id).first()
    if not acta:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    
    pdf_content = pdf_service.generate_comunion_pdf(acta)
    filename = f"partida_comunion_{acta.nombre}_{acta.apellidos}.pdf".replace(" ", "_").upper()
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.put("/comuniones/{id}", response_model=schemas.ActaComunion)
def update_comunion(
    *,
    db: Session = Depends(get_db),
    id: int,
    acta_in: schemas.ActaComunionCreate
) -> Any:
    """Actualizar un acta de primera comunión"""
    obj = db.query(models.ActaComunion).filter(models.ActaComunion.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    
    update_data = acta_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(obj, field, value)
    
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/comuniones/{id}")
def delete_comunion(id: int, db: Session = Depends(get_db)):
    obj = db.query(models.ActaComunion).filter(models.ActaComunion.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    db.delete(obj)
    db.commit()
    return {"status": "ok"}
