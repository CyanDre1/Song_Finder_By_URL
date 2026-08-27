import os
import shutil
from pathlib import Path

import acoustid
import requests
from dotenv import load_dotenv

from fingerprint.acrcloud import identify_song_with_acrcloud
from fingerprint.audd import identify_song_with_audd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

_PLACEHOLDER_KEY = "your_acoustid_api_key_here"

FPCALC_FALLBACKS = [
    Path(os.environ.get("CHROMAPRINT_DIR", "C:/Users/T450/AppData/Local/Programs/chromaprint"))
    / "chromaprint-fpcalc-1.6.1-windows-x86_64"
    / "fpcalc.exe",
    Path("C:/Program Files/chromaprint/bin/fpcalc.exe"),
    Path("C:/Program Files (x86)/chromaprint/bin/fpcalc.exe"),
]


def _find_fpcalc() -> str:
    env = os.environ.get("FPCALC", "").strip()
    if env and Path(env).is_file():
        return env
    found = shutil.which("fpcalc")
    if found:
        return found
    for candidate in FPCALC_FALLBACKS:
        if candidate.is_file():
            return str(candidate)
    raise FingerprintError(
        "fpcalc (chromaprint) tidak ditemukan. Download dari acoustid.org/chromaprint."
    )


class IdentificationError(Exception):
    """Base error for all identification failures."""


class SongNotFoundError(IdentificationError):
    """No matching song in the fingerprint database."""


class FingerprintError(IdentificationError):
    """Audio fingerprint could not be generated."""


class IdentificationServiceError(IdentificationError):
    """AcoustID API failed or timed out."""


def _get_api_key() -> str:
    key = os.getenv("ACOUSTID_API_KEY", "").strip()
    if not key or key == _PLACEHOLDER_KEY:
        raise IdentificationServiceError(
            "ACOUSTID_API_KEY belum diisi di file .env."
        )
    return key


def _pick_best(results) -> dict | None:
    for result in sorted(results, key=lambda r: r.get("score", 0), reverse=True):
        recordings = result.get("recordings", [])
        if not recordings:
            continue
        recording = recordings[0]
        title = recording.get("title")
        if not title:
            continue
        artists = recording.get("artists", [])
        artist = artists[0].get("name", "Unknown") if artists else "Unknown"
        return {
            "title": title,
            "artist": artist,
            "score": result.get("score", 0),
        }
    return None


def identify_song(audio_path: str) -> dict:
    api_key = _get_api_key()
    os.environ["FPCALC"] = _find_fpcalc()
    try:
        response = acoustid.match(api_key, audio_path, parse=False)
    except acoustid.FingerprintGenerationError as exc:
        raise FingerprintError("Gagal membuat fingerprint audio.") from exc
    except (acoustid.WebServiceError, requests.RequestException) as exc:
        raise IdentificationServiceError(
            "Layanan identifikasi sedang bermasalah."
        ) from exc

    results = response.get("results", []) if isinstance(response, dict) else []
    song = _pick_best(results)
    if song is None:
        song = identify_song_with_acrcloud(audio_path)
    if song is None:
        song = identify_song_with_audd(audio_path)
    if song is None:
        raise SongNotFoundError("Lagu tidak ditemukan.")
    return song