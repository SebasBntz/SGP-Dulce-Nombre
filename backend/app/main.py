from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys
import time
import logging

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.session import engine
from app.models.all_models import Base

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

from app.core.security import get_password_hash
from app.models.all_models import Usuario, UsuarioRol
from app.db.session import SessionLocal

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    
    # Auto-create admin if database is empty (First Run Scenario)
    db = SessionLocal()
    try:
        admin_exists = db.query(Usuario).first()
        if not admin_exists:
            logger.info("First run detected. Creating default admin user...")
            default_admin = Usuario(
                email="admin@parroquia.com",
                password_hash=get_password_hash("admin123456"),
                nombre_completo="Administrador Maestro",
                rol=UsuarioRol.ADMIN,
                is_active=True,
                activo=True,
                usuario="admin"
            )
            db.add(default_admin)
            db.commit()
    except Exception as e:
        logger.error(f"Error creating default admin: {e}")
    finally:
        db.close()
        
    yield
    # Shutdown: Clean up if needed
    logger.info("Shutting down...")

app = FastAPI(
    title="Parroquia Records System",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# =============================================
# 1. HEALTH CHECK - Debe ir ANTES de todo mount
# =============================================
@app.get("/health")
def health_check():
    return {"status": "ok", "project": "Parroquia Records System"}

# =============================================
# 2. MIDDLEWARE
# =============================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    if request.url.path.startswith("/health") or request.url.path.startswith("/static"):
        return await call_next(request)
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

# =============================================
# 3. CORS
# =============================================
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# =============================================
# 4. API ROUTES - Antes del mount estático
# =============================================
app.include_router(api_router, prefix=settings.API_V1_STR)

# =============================================
# 5. ARCHIVOS ESTÁTICOS (subidas)
# =============================================
static_dir = Path(settings.BASE_DATA_DIR) / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# =============================================
# 6. FRONTEND - Al FINAL porque "/" captura todo
# =============================================
def get_project_root():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent

PROJECT_ROOT = get_project_root()
frontend_path = PROJECT_ROOT / "frontend"

if frontend_path.is_dir():
    logger.info(f"Montando frontend desde: {frontend_path}")
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
else:
    logger.warning(f"No se encontró la carpeta frontend en: {frontend_path}")
