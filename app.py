import logging
import os

from flask import Flask, jsonify, render_template, request

logging.basicConfig(level=logging.INFO)

from extractor.video_extractor import (
    AudioConversionError,
    ExtractionError,
    UnsupportedPlatformError,
    VideoUnavailableError,
    extract_audio,
)
from fingerprint.identify import (
    FingerprintError,
    IdentificationServiceError,
    SongNotFoundError,
    identify_song,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/identify", methods=["POST"])
def api_identify():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    if not url:
        return (
            jsonify(
                {"status": "error", "message": "Platform tidak didukung."}
            ),
            400,
        )

    audio_path = None
    try:
        audio_path = extract_audio(url)
        song = identify_song(audio_path)
        return jsonify({"status": "success", "song": song})
    except UnsupportedPlatformError:
        return (
            jsonify({"status": "error", "message": "Platform tidak didukung."}),
            400,
        )
    except VideoUnavailableError:
        app.logger.exception("VideoUnavailableError")
        return (
            jsonify(
                {"status": "error", "message": "Video tidak dapat diakses."}
            ),
            400,
        )
    except (AudioConversionError, ExtractionError):
        app.logger.exception("ExtractionError")
        return (
            jsonify(
                {"status": "error", "message": "Gagal memproses video."}
            ),
            500,
        )
    except SongNotFoundError:
        app.logger.exception("SongNotFoundError")
        return (
            jsonify({"status": "error", "message": "Lagu tidak ditemukan."}),
            404,
        )
    except (FingerprintError, IdentificationServiceError):
        app.logger.exception("IdentificationServiceError")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Layanan identifikasi sedang bermasalah.",
                }
            ),
            503,
        )
    except Exception:
        app.logger.exception("UnexpectedError")
        return (
            jsonify(
                {"status": "error", "message": "Gagal memproses video."}
            ),
            500,
        )
    finally:
        if audio_path:
            try:
                os.remove(audio_path)
            except OSError:
                pass


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
