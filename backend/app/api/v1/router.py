from fastapi import APIRouter
from app.api.v1.routes import auth, actas, parroquia_mgmt

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(actas.router, prefix="/actas", tags=["actas"])
api_router.include_router(parroquia_mgmt.router, prefix="/parroquia", tags=["parroquia"])
