# Recetario IA

Herramienta diseñada para automatizar la extracción de recetas de cocina desde videos (YouTube, TikTok) mediante procesamiento con Inteligencia Artificial.

El sistema descarga el video de la fuente proporcionada (o permite la carga manual del archivo), separa el contenido multimedia si es necesario, y lo envía a la API de Gemini de Google para estructurar la receta en ingredientes y pasos detallados. Incluye una base de datos local para almacenar y editar las recetas procesadas.

## Estructura del Proyecto

* `app.py`: Interfaz de usuario construida con Streamlit. Contiene las pestañas de extracción de recetas y el administrador/editor de recetas guardadas.
* `video_processor.py`: Motor de descarga y procesamiento. Maneja pytubefix para YouTube, yt-dlp como fallback, ensambla video/audio mediante subprocess con FFmpeg y maneja la comunicación con la SDK de Google GenAI.
* `database.py`: Gestión de la base de datos local SQLite (`recetas.db`). Contiene las funciones CRUD para persistir la información.
* `requirements.txt`: Dependencias de librerías de Python.
* `packages.txt`: Dependencias del sistema operativo (requerido para despliegues en Streamlit Community Cloud para instalar ffmpeg).

## Requisitos Previos

Para ejecutar este proyecto en un entorno local, se requiere:

1. **Python 3.12** o superior.
2. **FFmpeg** instalado en el sistema operativo y agregado a la variable PATH.
3. Una clave de API válida de Google Gemini (GEMINI_API_KEY).

## Instalación y Pruebas Locales

1. Clona este repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd recetario-ia
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   ```

3. Instala las dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura tus variables de entorno:
   Crea un archivo `.env` en la raíz del proyecto y añade tu clave:
   ```text
   GEMINI_API_KEY="TU_CLAVE_AQUI"
   ```

5. Ejecuta la aplicación:
   ```bash
   streamlit run app.py
   ```

La aplicación se abrirá automáticamente en tu navegador por defecto (usualmente en `http://localhost:8501`).

## Despliegue en la Nube

El repositorio está optimizado para desplegarse directamente en **Streamlit Community Cloud**. El archivo `packages.txt` asegurará la instalación del paquete de sistema `ffmpeg` sin configuraciones adicionales. Recuerda configurar el secreto `GEMINI_API_KEY` en el panel de control del host antes de iniciar el despliegue.
