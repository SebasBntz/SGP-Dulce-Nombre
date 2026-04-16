# Parroquia Records System - Backend

Este es el backend para el Sistema de Gestión de Actas Parroquiales. Está construido con FastAPI y usa PostgreSQL como base de datos.

## Requisitos previos

- Python 3.9+ instalado
- PostgreSQL 13+ instalado y ejecutándose localmente
- Entorno virtual (recomendado)

## Configuración inicial

1. **Variable de entorno**:
   Asegúrate de que el archivo `.env` tenga las credenciales correctas de tu PostgreSQL local:
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_SERVER`
   - `POSTGRES_DB`

2. **Instalar dependencias**:

   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic-settings python-jose[cryptography] passlib[argon2] python-multipart psycopg2-binary python-dotenv
   ```

3. **Inicializar Base de Datos**:
   Este comando creará la base de datos en PostgreSQL y aplicará el esquema:
   ```bash
   python init_db.py
   ```

## Ejecución del Servidor

Para iniciar la API y servir el frontend estático:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000/api/v1`.
La documentación interactiva (Swagger UI) está en `http://localhost:8000/docs`.

## Estructura del Proyecto

- `app/models/`: Definición de las actas (Bautizo, Matrimonio, etc.) y Usuarios.
- `app/api/v1/routes/actas.py`: Endpoints para crear y consultar actas.
- `app/schemas/`: Validaciones de datos con Pydantic.
- `database/`: Contiene el esquema SQL (`schema.sql`).
