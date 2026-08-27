# AGENTS.md

> Song Finder — paste a video URL, extract audio, identify the song. Frontend (Indonesian UI) + Flask backend.

---

## Quick start

```bash
# 1. shell
venv\Scripts\activate

# 2. (only if deps drift) install
pip install -r requirements.txt

# 3. run
python app.py        # → http://127.0.0.1:5000
```

- **Python** 3.11 · **Backend** Flask · no tests · no linter · no build step.
- Runtime deps are **system binaries**, not pip packages (see Gotchas).

---

## Architecture at a glance

```
        ┌───── templates/index.html ─────┐
        │  HTML form → fetch POST /api/identify
        └───────────────┬────────────────┘
                        ▼
        ┌───── app.py ─────┐
        │ POST /api/identify
        │   1. extract_audio(url)
        │   2. identify_song(audio_path)
        │   3. finally → delete temp audio
        └─────────┬────────┘
          ┌───────┴──────────────┐
          ▼                      ▼
   extractor/         fingerprint/
   video_extractor  identify.py
      │  yt-dlp      AcoustID
      │  ffmpeg      │
      └─► WAV to temp ──► {title,artist,score}
                           ─ ACRCloud (fallback)
                           ─ AudD (fallback)
```

- `extractor/video_extractor.py` → `extract_audio(url) -> str` (path to WAV).
- `fingerprint/identify.py` → `identify_song(path) -> dict`, chains AcoustID → ACRCloud → AudD.
- `fingerprint/acrcloud.py`, `audd.py` → swappable backends; each cleans up its own slices.
- Stateless: no DB, no persistent storage beyond `.env`.

---

## API contract

`POST /api/identify` · `Content-Type: application/json`

```json
{ "url": "https://www.youtube.com/watch?v=..." }
```

Success `200`:
```json
{ "status": "success", "song": { "title": "...", "artist": "...", "score": 0.95 } }
```

| Map | Condition | HTTP | message (id) |
|-----|-----------|------|--------------|
| 400 | URL invalid / platform unsupported | 400 | "Platform tidak didukung." |
| 400 | Video private / expired / unavailable | 400 | "Video tidak dapat diakses." |
| 500 | extraction / conversion failure | 500 | "Gagal memproses video." |
| 404 | no match across all backends | 404 | "Lagu tidak ditemukan." |
| 503 | AcoustID API / network fault | 503 | "Layanan identifikasi sedang bermasalah." |

---

## Gotchas (agents miss these)

- **ffmpeg** must be on PATH. The code also checks fallbacks `C:/ffmpeg/bin/ffmpeg.exe`, `C:/Program Files/ffmpeg/bin/ffmpeg.exe`, `C:/Program Files (x86)/ffmpeg/bin/ffmpeg.exe`. yt-dlp alone is **not** enough.
- **Do NOT `pip install chromaprint`** — it's an unrelated terminal-color lib (PyPI name collision). pyacoustid calls the `fpcalc` binary. `fingerprint/identify.py:_find_fpcalc()` resolves it from:
  1. `FPCALC` env var → then →
  2. `shutil.which("fpcalc")` → then →
  3. fallbacks: `%CHROMAPRINT_DIR%/chromaprint-fpcalc-1.6.1-windows-x86_64/fpcalc.exe`, `C:/Program Files/chromaprint/bin/fpcalc.exe`, `C:/Program Files (x86)/chromaprint/bin/fpcalc.exe`.
  Get the official chromaprint release zip from acoustid.org.
- **YouTube 403**: extractor sets `extractor_args.youtube.player_client = ["android","web_safari"]` (already in code, do not remove).
- **Audio normalization**: ffmpeg outputs **44100 Hz mono PCM WAV** (`-ar 44100 -ac 1 -vn`). Keep this for fingerprint accuracy.
- **Temp hygiene**: `app.py` deletes the WAV in a `finally`; the extractor drops the pre-WAV download; each backend deletes its 12-s slices. Don't "help" by nuking `temp/` mid-run — you'll break a live identify.
- **`.env` is gitignored** (contains real AcoustID + ACRCloud + AudD keys). It is loaded via `python-dotenv` at import time in `identify.py`, `acrcloud.py`, `audd.py`. Missing/placeholder keys raise `IdentificationServiceError` (503), not a crash.
- Only AcoustID is the **primary** matcher; ACRCloud/AudD are transparent fallbacks. ACRCloud keys are needed in `.env` for that fallback to actually run.
- **AudD reuses acrcloud internals**: `audd.py` imports `_slice_segment`, `SEGMENT_SECONDS`, `MAX_SEGMENTS`, and `TEMP_DIR` from `fingerprint/acrcloud.py`. If you change segment slicing, you affect both backends.

---

## Supported sources

Domains accepted by `SUPPORTED_DOMAINS` (`extractor/video_extractor.py:28`):
YouTube (youtube.com, youtu.be) · TikTok · Instagram · Facebook · fb.watch · X/Twitter · Pinterest (pinterest.com, pin.it) · snapchat.com · likee.video.

---

## Dev notes

- `.agent/` holds the spec (Indonesian): `prd.md`, `design.md`, `task-instruction.md`, `tasklist.md` — consult for intent; `tasklist.md` is the status tracker (update % as you work).
- Manual testing list (`.agent/tasklist.md §6`): YouTube Shorts, TikTok, Instagram Reels, invalid URL, obscure-song 404 path. No automated suite exists.
- No `README.md` yet (task 7.1 in the tracker) — this file is the runbook until then.
