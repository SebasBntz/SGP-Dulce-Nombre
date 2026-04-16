# ⛪ Sistema de Gestión Parroquial (Actas y Registros)

Un moderno y ligero Sistema de Gestión Parroquial diseñado para automatizar y organizar el control de sacramentos, feligreses y finanzas de la parroquia. 

Este sistema proporciona una interfaz intuitiva y rápida para que párrocos y secretarias puedan registrar, buscar y certificar actas sacramentales al instante, con capacidades de autogeneración de actas en PDF listas para imprimir validamente.

## ✨ Características Principales

* **📜 Gestión de Sacramentos (Actas):** 
  * Registro detallado de **Bautizos, Confirmaciones, Primeras Comuniones y Matrimonios**.
  * Búsqueda global instantánea por número de folio, libro o nombre.
  * Generación y exportación de certificados/actas a PDF en un clic.
* **👥 Directorio Comunitario:** 
  * Base de datos de feligreses y sacerdotes.
  * Creación y administración de **Grupos Parroquiales**.
* **💰 Finanzas y Aportes:** 
  * Gestión de donaciones, diezmos y ofrendas.
  * Dashboard inteligente con gráficos de ingresos mensuales generados dinámicamente.
* **🛡️ Seguridad y Respaldo:** 
  * Sistema de autenticación JWT para usuarios administradores.
  * Panel dedicado para generar **Respaldos de Base de Datos** de forma sencilla.

## 🛠️ Tecnologías Utilizadas

* **Frontend:** HTML5, Vanilla JavaScript, CSS3 (Diseño responsivo / SPA), Chart.js (Gráficos visuales).
* **Backend:** Python 3, FastAPI, SQLAlchemy (ORM).
* **Librerías Extra:** FPDF (Generación de Reportes y PDFs).
* **Base de Datos:** PostgreSQL / SQLite (Para entorno local).
* **Empaquetado:** Preparado para funcionar de manera local, web, o envolverse vía Electron como app de escritorio.

## 🚀 Instalación y Ejecución Local

1. **Clonar el repositorio y entrar a la capeta:**
   ```bash
   git clone https://github.com/tu-usuario/proyecto-parroquia.git
   cd proyecto-parroquia/backend
   ```

2. **Crear e inicializar el entorno virtual (Recomendado):**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate   # En Windows
   ```

3. **Instalar dependencias del servidor:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicializar la BD y crear Administrador:**
   ```bash
   python init_db.py
   python create_admin.py
   ```

5. **Iniciar el servidor web:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   > Finalmente, abre tu navegador web en `http://localhost:8000` e inicia sesión con las credenciales creadas.

## 📄 Licencia
Este proyecto es de uso interno para la Parroquia Dulce Nombre de Jesús. Todos los derechos reservados.