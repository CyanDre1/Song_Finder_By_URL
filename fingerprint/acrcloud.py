import base64
import hashlib
import hmac
import os
import subprocess
import time
import uuid
import wave
from pathlib import Path

import requests
from dotenv import load_dotenv

from extractor.video_extractor import _find_ffmpeg

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

TEMP_DIR = PROJECT_ROOT / "temp"
SEGMENT_SECONDS = 12
MAX_SEGMENTS = 6
MIN_SCORE = 20


class ACRCloudNotConfiguredError(Exception):
    """ACRCloud credentials are missing from .env."""


def _get_config() -> tuple[str, str, str]:
    host = os.getenv("ACRCLOUD_HOST", "").strip()
    key = os.getenv("ACRCLOUD_ACCESS_KEY", "").strip()
    secret = os.getenv("ACRCLOUD_ACCESS_SECRET", "").strip()
    if not host or not key or not secret:
        raise ACRCloudNotConfiguredError("ACRCloud config belum diisi di .env.")
    return host, key, secret


def _duration_seconds(wav_path: Path) -> int:
    with wave.open(str(wav_path), "rb") as wav:
        return int(wav.getnframes() / wav.getframerate())


def _slice_segment(wav_path: Path, start: int) -> Path | None:
    ffmpeg = _find_ffmpeg()
    out_path = TEMP_DIR / f"seg_{uuid.uuid4().hex[:10]}.wav"
    proc = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-ss",
            str(start),
            "-t",
            str(SEGMENT_SECONDS),
            "-i",
            str(wav_path),
            "-ar",
            "44100",
            "-ac",
            "1",
            str(out_path),
        ],
        capture_output=True,
    )
    if proc.returncode != 0 or not out_path.is_file():
        out_path.unlink(missing_ok=True)
        return None
    return out_path


def _sign(key: str, secret: str, timestamp: str) -> str:
    string_to_sign = (
        "POST\n"
        "/v1/identify\n"
        f"{key}\n"
        "audio\n"
        "1\n"
        f"{timestamp}"
    )
    digest = hmac.new(
        secret.encode("ascii"),
        string_to_sign.encode("ascii"),
        digestmod=hashlib.sha1,
    ).digest()
    return base64.b64encode(digest).decode("ascii")


def _recognize_segment(
    segment_path: Path, host: str, key: str, secret: str
) -> dict | None:
    timestamp = str(time.time())
    sample = segment_path.read_bytes()
    files = [("sample", (segment_path.name, sample, "audio/wav"))]
    data = {
        "access_key": key,
        "sample_bytes": str(len(sample)),
        "timestamp": timestamp,
        "signature": _sign(key, secret, timestamp),
        "data_type": "audio",
        "signature_version": "1",
    }
    resp = requests.post(
        f"https://{host}/v1/identify", files=files, data=data, timeout=30
    )
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("status", {}).get("code") != 0:
        return None
    music = payload.get("metadata", {}).get("music", [])
    if not music:
        return None
    top = music[0]
    title = top.get("title")
    if not title:
        return None
    artists = top.get("artists", [])
    artist = artists[0].get("name", "Unknown") if artists else "Unknown"
    score = top.get("score", 0)
    return {"title": title, "artist": artist, "score": score}


def identify_song_with_acrcloud(audio_path: str) -> dict | None:
    """Recognize audio via ACRCloud. Returns the highest-scoring match or None."""
    try:
        host, key, secret = _get_config()
    except ACRCloudNotConfiguredError:
        return None

    wav_path = Path(audio_path)
    duration = _duration_seconds(wav_path)
    best: dict | None = None
    try:
        for start in range(0, duration, SEGMENT_SECONDS):
            if start // SEGMENT_SECONDS >= MAX_SEGMENTS:
                break
            segment = _slice_segment(wav_path, start)
            if segment is None:
                continue
            try:
                song = _recognize_segment(segment, host, key, secret)
            finally:
                segment.unlink(missing_ok=True)
            if song is None or song.get("score", 0) < MIN_SCORE:
                continue
            if best is None or song.get("score", 0) > best.get("score", 0):
                best = song
    except (requests.RequestException, subprocess.SubprocessError, OSError):
        return None
    return best
