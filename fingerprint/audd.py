import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from fingerprint.acrcloud import (
    MAX_SEGMENTS,
    SEGMENT_SECONDS,
    TEMP_DIR,
    _slice_segment,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class AudDNotConfiguredError(Exception):
    """AudD API token is missing from .env."""


def _get_token() -> str:
    token = os.getenv("AUDD_API_TOKEN", "").strip()
    if not token:
        raise AudDNotConfiguredError("AUDD_API_TOKEN belum diisi di .env.")
    return token


def _recognize_segment(segment_path: Path, token: str) -> dict | None:
    resp = requests.post(
        "https://api.audd.io/",
        files={
            "file": (
                segment_path.name,
                segment_path.read_bytes(),
                "audio/wav",
            )
        },
        data={"api_token": token},
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("status") != "success":
        return None
    result = payload.get("result")
    if not result or not isinstance(result, dict):
        return None
    title = result.get("title")
    if not title:
        return None
    artist = result.get("artist") or "Unknown"
    return {"title": title, "artist": artist, "score": 0}


def identify_song_with_audd(audio_path: str) -> dict | None:
    """Recognize audio via AudD. Returns the first match or None."""
    try:
        token = _get_token()
    except AudDNotConfiguredError:
        return None

    wav_path = Path(audio_path)
    if not wav_path.is_file():
        return None
    try:
        for start in range(0, 3600, SEGMENT_SECONDS):
            if start // SEGMENT_SECONDS >= MAX_SEGMENTS:
                break
            segment = _slice_segment(wav_path, start)
            if segment is None:
                continue
            try:
                song = _recognize_segment(segment, token)
            finally:
                segment.unlink(missing_ok=True)
            if song:
                return song
    except (requests.RequestException, OSError):
        return None
    return None