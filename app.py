from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp
import os
import uuid
import threading
import time

app = Flask(__name__)

DOWNLOAD_FOLDER = "/tmp/videos"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def limpiar_archivos_viejos():
    while True:
        time.sleep(300)
        ahora = time.time()
        for f in os.listdir(DOWNLOAD_FOLDER):
            ruta = os.path.join(DOWNLOAD_FOLDER, f)
            if ahora - os.path.getmtime(ruta) > 600:
                os.remove(ruta)

threading.Thread(target=limpiar_archivos_viejos, daemon=True).start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/info", methods=["POST"])
def info():
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "URL vacía"}), 400

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "titulo": info.get("title", "Video"),
                "thumbnail": info.get("thumbnail", ""),
                "duracion": info.get("duration", 0),
                "plataforma": info.get("extractor_key", ""),
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/descargar", methods=["POST"])
def descargar():
    data = request.get_json()
    url = data.get("url", "").strip()
    formato = data.get("formato", "mp4")

    if not url:
        return jsonify({"error": "URL vacía"}), 400

    file_id = str(uuid.uuid4())

    if formato == "mp3":
        output_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp3")
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path.replace(".mp3", ".%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
        }
        final_path = output_path
        mime = "audio/mpeg"
        ext = "mp3"
    else:
        output_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": output_path.replace(".mp4", ".%(ext)s"),
            "merge_output_format": "mp4",
            "quiet": True,
        }
        final_path = output_path
        mime = "video/mp4"
        ext = "mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            titulo = info.get("title", "video")

        archivos = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(file_id)]
        if not archivos:
            return jsonify({"error": "No se pudo descargar el archivo"}), 500

        archivo_real = os.path.join(DOWNLOAD_FOLDER, archivos[0])
        nombre_limpio = "".join(c for c in titulo if c.isalnum() or c in " _-")[:50]
        nombre_descarga = f"{nombre_limpio}.{ext}"

        return send_file(
            archivo_real,
            mimetype=mime,
            as_attachment=True,
            download_name=nombre_descarga
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
