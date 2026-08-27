import re
import shutil
import subprocess
import uuid
from pathlib import Path

import yt_dlp

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMP_DIR = PROJECT_ROOT / "temp"

FFMPEG_FALLBACKS = [
    Path("C:/ffmpeg/bin/ffmpeg.exe"),
    Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
    Path("C:/Program Files (x86)/ffmpeg/bin/ffmpeg.exe"),
]


def _find_ffmpeg() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    for candidate in FFMPEG_FALLBACKS:
        if candidate.is_file():
            return str(candidate)
    raise AudioConversionError("ffmpeg tidak ditemukan di PATH.")

SUPPORTED_DOMAINS = {
    "youtube.com",
    "youtu.be",
    "tiktok.com",
    "instagram.com",
    "facebook.com",
    "fb.watch",
    "x.com",
    "twitter.com",
    "pinterest.com",
    "pin.it",
    "snapchat.com",
    "likee.video",
}

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


class ExtractionError(Exception):
    """Base error for all extraction failures."""


class UnsupportedPlatformError(ExtractionError):
    """URL is invalid or the platform is not supported."""


class VideoUnavailableError(ExtractionError):
    """Video cannot be accessed (private, expired, or not found)."""


class AudioConversionError(ExtractionError):
    """Audio stream downloaded but conversion to WAV failed."""


def _extract_domain(url: str) -> str:
    match = re.search(r"://([^/]+)", url)
    return match.group(1).lower() if match else ""


def _is_supported(url: str) -> bool:
    domain = _extract_domain(url)
    return any(
        domain == base or domain.endswith("." + base) for base in SUPPORTED_DOMAINS
    )


def _find_downloaded(base_path: Path) -> Path | None:
    for match in TEMP_DIR.glob(f"{base_path.name}.*"):
        if match.suffix != ".wav":
            return match
    return None


def extract_audio(url: str) -> str:
    url = url.strip()
    if not _URL_RE.match(url) or not _is_supported(url):
        raise UnsupportedPlatformError("URL tidak valid atau platform tidak didukung.")

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    base_path = TEMP_DIR / f"audio_{uuid.uuid4().hex[:12]}"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{base_path}.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "socket_timeout": 30,
        "retries": 10,
        "fragment_retries": 10,
        "file_access_retries": 5,
        "extractor_args": {"youtube": {"player_client": ["android", "web_safari"]}},
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
    except yt_dlp.utils.UnsupportedError as exc:
        raise UnsupportedPlatformError("Platform tidak didukung.") from exc
    except yt_dlp.utils.DownloadError as exc:
        raise VideoUnavailableError("Video tidak dapat diakses.") from exc

    downloaded = _find_downloaded(base_path)
    if downloaded is None:
        raise ExtractionError("Gagal memproses video.")

    wav_path = base_path.with_suffix(".wav")
    try:
        subprocess.run(
            [
                _find_ffmpeg(),
                "-y",
                "-i",
                str(downloaded),
                "-ar",
                "44100",
                "-ac",
                "1",
                "-vn",
                str(wav_path),
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        raise AudioConversionError("Gagal mengonversi audio.") from exc
    finally:
        downloaded.unlink(missing_ok=True)

    return str(wav_path)
