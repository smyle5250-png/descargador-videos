from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp
import os
import uuid
import threading
import time

app = Flask(__name__)

DOWNLOAD_FOLDER = "/tmp/videos"
COOKIES_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def limpiar_archivos_viejos():
    while True:
        time.sleep(300)
        ahora = time.time()
        for f in os.listdir(DOWNLOAD_FOLDER):
            ruta = os.path.join(DOWNLOAD_FOLDER, f)
            try:
                if ahora - os.path.getmtime(ruta) > 600:
                    os.remove(ruta)
            except:
                pass

threading.Thread(target=limpiar_archivos_viejos, daemon=True).start()

def get_ydl_opts(extra={}):
    opts = {
        "quiet": True,
        "no_warnings": True,
    }
    if os.path.exists(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE
    opts.update(extra)
    return opts

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/info", methods=["POST"])
def info():
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "URL vacía"}), 400

    try:
        with yt_dlp.YoutubeDL(get_ydl_opts({"skip_download": True})) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "titulo": info.get("title", "Video"),
                "thumbnail": info.get("thumbnail", ""),
                "duracion": info.get("duration", 0),
                "plataforma": info.get("extractor_key", "Desconocido"),
                "autor": info.get("uploader", ""),
            })
    except Exception as e:
        return jsonify({"error": "No se pudo obtener el video. Verificá que el link sea correcto y que el video sea público."}), 400

@app.route("/descargar", methods=["POST"])
def descargar():
    data = request.get_json()
    url = data.get("url", "").strip()
    formato = data.get("formato", "mp4")

    if not url:
        return jsonify({"error": "URL vacía"}), 400

    file_id = str(uuid.uuid4())

    if formato == "mp3":
        extra = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
        ext = "mp3"
        mime = "audio/mpeg"
    else:
        extra = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s"),
            "merge_output_format": "mp4",
        }
        ext = "mp4"
        mime = "video/mp4"

    try:
        with yt_dlp.YoutubeDL(get_ydl_opts(extra)) as ydl:
            info = ydl.extract_info(url, download=True)
            titulo = info.get("title", "video")

        archivos = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(file_id)]
        if not archivos:
            return jsonify({"error": "No se pudo descargar el archivo"}), 500

        archivo_real = os.path.join(DOWNLOAD_FOLDER, archivos[0])
        nombre_limpio = "".join(c for c in titulo if c.isalnum() or c in " _-")[:50].strip()
        nombre_descarga = f"{nombre_limpio or 'video'}.{ext}"

        return send_file(
            archivo_real,
            mimetype=mime,
            as_attachment=True,
            download_name=nombre_descarga
        )

    except Exception as e:
        return jsonify({"error": "No se pudo descargar. El video puede ser privado o no compatible."}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
