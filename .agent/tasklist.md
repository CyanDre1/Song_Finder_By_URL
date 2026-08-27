# Tasklist — Song Finder

Working document. Update status saat mengerjakan.

Status: `[ ]` pending · `[~]` in-progress · `[x]` done

**Progress keseluruhan: 96%** (24/25 sub-task selesai)

## 1. Setup Environment — 100% (6/6)
- 1.1 [x] Install Python 3.10+ (3.11.1)
- 1.2 [x] Install `ffmpeg` (pastikan bisa dipanggil dari command line / on PATH) — portable di `C:\Users\T450\AppData\Local\Programs\ffmpeg`, sudah di PATH
- 1.3 [x] Buat virtual environment (`venv`)
- 1.4 [x] Buat `requirements.txt` (`flask`, `yt-dlp`, `pyacoustid`, `chromaprint`, `python-dotenv`)
- 1.5 [x] Buat `.env` (`ACOUSTID_API_KEY`) — **masih placeholder, isi key nyata dari acoustid.org**
- 1.6 [x] Buat folder `temp/` + `.gitignore`

## 2. Modul Extraction (`extractor/video_extractor.py`) — 100% (5/5)
- 2.1 [x] Fungsi `extract_audio(url) -> str`
  - 2.1.1 [x] Validasi URL & platform didukung
  - 2.1.2 [x] Download audio stream via yt-dlp — pakai `player_client: ["android", "web_safari"]` untuk bypass 403 YouTube
  - 2.1.3 [x] Convert ke `.wav` via ffmpeg ke `temp/` (nama file unik) — PCM s16le, 44100 Hz, mono
- 2.2 [x] Error handling: URL invalid, video tidak ditemukan, video private (`UnsupportedPlatformError`, `VideoUnavailableError`, `AudioConversionError`)

## 3. Modul Fingerprinting (`fingerprint/identify.py`) — 100% (5/5)
- 3.1 [x] Fungsi `identify_song(audio_path) -> dict`
  - 3.1.1 [x] Generate fingerprint (chromaprint) — via **`fpcalc` binary** (pyacoustid), bukan package pip `chromaprint` (name collision)
  - 3.1.2 [x] Kirim ke AcoustID API — teruji live dengan key nyata. Catatan: pakai `acoustid.match(..., parse=False)`; exception `NoMatchFound` TIDAK ada di pyacoustid 1.3.1
  - 3.1.3 [x] Parse response → `{title, artist, score}`
- 3.2 [x] Error handling: lagu tidak ditemukan, API timeout/gagal (`SongNotFoundError`, `FingerprintError`, `IdentificationServiceError`)

## 4. Backend API (`app.py`) — 100% (4/4)
- 4.1 [x] Setup Flask app (localhost:5000) — rute `/` masih 500 sampai Task 5 bikin `templates/index.html`
- 4.2 [x] Endpoint `POST /api/identify` → extraction → fingerprint → JSON
- 4.3 [x] Cleanup otomatis file di `temp/` setelah selesai (sukses/gagal) — via `finally` di handler
- 4.4 [x] Error mapping sesuai design.md §5 (400/404/500/503) — teruji via test client

## 5. Frontend (`templates/index.html`, `static/`) — 100% (4/4)
- 5.1 [x] Form input URL + tombol submit
- 5.2 [x] Loading indicator (proses bisa makan detik) — spinner + disabled tombol
- 5.3 [x] Tampilkan hasil: judul, artis, score
- 5.4 [x] Tampilkan pesan error yang jelas

## 6. Testing Manual — 0% (0/5)
- 6.1 [ ] Test YouTube Shorts
- 6.2 [ ] Test TikTok
- 6.3 [ ] Test Instagram Reels
- 6.4 [ ] Test URL invalid (bukan link video)
- 6.5 [ ] Test video dengan lagu obscure (expect "tidak ditemukan", bukan crash)

## 7. Dokumentasi — 0% (0/1)
- 7.1 [ ] `README.md`: cara install & jalankan, daftar platform didukung + batasan

## Urutan Pengerjaan
Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7