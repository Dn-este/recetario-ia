import streamlit as st
import os
from dotenv import load_dotenv
from database import init_db, guardar_receta, obtener_recetas, actualizar_receta, eliminar_receta
from video_processor import descargar_video, extraer_receta

load_dotenv()

st.set_page_config(page_title="Recetario IA", layout="wide")

# Inicializar BD
init_db()

st.title("🍳 Extractor de Recetas IA")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "tu_clave_aqui_reemplazar":
    st.warning("⚠️ Configura tu GEMINI_API_KEY en el archivo .env")
    st.stop()

tab_nueva, tab_lista = st.tabs(["Extraer Receta", "Mis Recetas"])

with tab_nueva:
    st.info("TikTok bloquea descargas a menudo. Si falla la URL, descarga el video manualmente y súbelo aquí.")
    
    url_input = st.text_input("1. Pega la URL del video (YouTube funciona mejor):")
    archivo_subido = st.file_uploader("2. O sube el video directamente (.mp4)", type=["mp4", "mov"])
    
    titulo_input = st.text_input("Título de la receta (Opcional):")
    
    if st.button("Procesar Video"):
        video_path = None
        
        if archivo_subido is not None:
            # Guardar el archivo subido
            os.makedirs("downloads", exist_ok=True)
            video_path = os.path.abspath(os.path.join("downloads", "video_subido.mp4"))
            with open(video_path, "wb") as f:
                f.write(archivo_subido.read())
            st.success("Video cargado desde archivo!")
            
        elif url_input:
            with st.spinner("Descargando video desde URL..."):
                try:
                    video_path = descargar_video(url_input)
                    st.success("Video descargado!")
                except Exception as e:
                    st.error(f"Error al descargar: {e}")
                    st.stop()
        else:
            st.error("Proporciona una URL o sube un archivo.")
            st.stop()
            
        if video_path:
            with st.spinner("Analizando con Gemini 1.5 Pro..."):
                try:
                    resultado = extraer_receta(video_path, api_key)
                    contenido = resultado["texto"]
                    st.markdown("### Resultado:")
                    st.markdown(contenido)
                    
                    titulo_final = titulo_input.strip() if titulo_input else ""
                    if not titulo_final:
                        # Extraer el título del markdown generado por la IA (busca el primer título #)
                        lineas = [line.strip() for line in contenido.split('\n') if line.strip()]
                        for line in lineas:
                            if line.startswith('#'):
                                titulo_final = line.lstrip('# ').strip()
                                break
                        if not titulo_final:
                            titulo_final = lineas[0] if lineas else "Receta sin título"
                    
                    guardar_receta(titulo_final, url_input, "Extraído", contenido)
                    st.success("Receta guardada en la base de datos.")
                except Exception as e:
                    st.error(f"Error en IA: {e}")

with tab_lista:
    recetas = obtener_recetas()
    if not recetas:
        st.info("Aún no tienes recetas guardadas.")
    else:
        for r in recetas:
            with st.expander(f"{r['titulo']} - {r['fecha']}"):
                ver_tab, editar_tab = st.tabs(["👁️ Ver Receta", "✏️ Editar"])
                
                with ver_tab:
                    st.write(f"**URL:** {r['url']}")
                    st.markdown(r['pasos'])
                
                with editar_tab:
                    nuevo_titulo = st.text_input("Título", value=r['titulo'], key=f"t_{r['id']}")
                    nuevos_pasos = st.text_area("Contenido de la receta (Markdown)", value=r['pasos'], height=400, key=f"p_{r['id']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Guardar Cambios", key=f"b_{r['id']}"):
                            actualizar_receta(r['id'], nuevo_titulo, nuevos_pasos)
                            st.success("¡Receta actualizada exitosamente!")
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Eliminar Receta", key=f"del_{r['id']}", type="primary"):
                            eliminar_receta(r['id'])
                            st.rerun()
