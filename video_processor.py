import os
from yt_dlp import YoutubeDL
from google import genai
import time

def descargar_video(url: str, output_path="downloads/video.mp4") -> str:
    """Descarga el video desde la URL y retorna la ruta del archivo."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        if "youtube.com" in url.lower() or "youtu.be" in url.lower():
            from pytubefix import YouTube
            
            # Intentar evadir el bot-block de servidores usando cliente diferente
            yt = YouTube(url, client='ANDROID')
            
            # Los Shorts de YouTube no tienen streams combinados. Bajamos por separado.
            v_stream = yt.streams.filter(type="video", file_extension="mp4").order_by("resolution").desc().first()
            a_stream = yt.streams.filter(type="audio").first()
            
            v_path = os.path.abspath(v_stream.download(output_path="downloads", filename="temp_vid.mp4"))
            a_path = os.path.abspath(a_stream.download(output_path="downloads", filename="temp_aud.mp4"))
            
            final_path = os.path.abspath(os.path.join("downloads", "video.mp4"))
            if os.path.exists(final_path):
                try:
                    os.remove(final_path)
                except:
                    pass
            
            ffmpeg_exe = r"C:\Users\PC\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
            if not os.path.exists(ffmpeg_exe):
                ffmpeg_exe = "ffmpeg"  # Usar el del sistema para la nube (Linux)
            
            import subprocess
            cmd = [ffmpeg_exe, "-y", "-i", v_path, "-i", a_path, "-c:v", "copy", "-c:a", "aac", final_path]
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if result.returncode != 0 or not os.path.exists(final_path):
                raise Exception(f"ffmpeg code: {result.returncode}, paths: {v_path}, {a_path}")
            
            try:
                os.remove(v_path)
                os.remove(a_path)
            except:
                pass
            
            return final_path
        else:
            # Fallback a yt-dlp para tiktok y otros
            ydl_opts = {
                'outtmpl': output_path,
                'noplaylist': True,
                'quiet': False
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return os.path.abspath(output_path)
    except Exception as e:
        raise Exception(f"Bloqueo detectado al intentar bajar la URL. Detalles: {e}\nPor favor usa la opción 2 y sube el .mp4 manual.")

def extraer_receta(video_path: str, api_key: str) -> dict:
    """Sube el video a Gemini y extrae la receta estructurada."""
    client = genai.Client(api_key=api_key)
    
    # 1. Subir video
    video_file = client.files.upload(
        path=video_path,
        config={'mime_type': 'video/mp4'}
    )
    
    # 2. Esperar procesamiento
    while video_file.state == "PROCESSING":
        time.sleep(2)
        video_file = client.files.get(name=video_file.name)
        
    if video_file.state == "FAILED":
        raise Exception("Fallo el procesamiento del video en Gemini.")
        
    # 3. Prompt de extracción
    prompt = """
    Eres un chef experto. Analiza el siguiente video de una receta.
    Extrae y genera un formato estructurado con:
    1. Título de la receta.
    2. Ingredientes (lista con cantidades exactas. Si no las dicen, deduce las medidas lógicas).
    3. Pasos de preparación (detallados paso a paso, incluyendo tiempos y acciones implícitas).
    
    Devuelve TODO el resultado en formato Markdown claro.
    Separa claramente la seccion de Ingredientes y la de Preparacion.
    """
    
    try:
        from google.genai import types
        video_part = types.Part.from_uri(file_uri=video_file.uri, mime_type=video_file.mime_type)
        
        response = client.models.generate_content(
            model='gemini-3.1-pro-preview',
            contents=[video_part, prompt]
        )
    except Exception as e:
        print(f"Fallo el principal: {e}. Intentando con 3.5-flash-lite...")
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=[video_part, prompt]
        )
    
    return {
        "texto": response.text
    }
