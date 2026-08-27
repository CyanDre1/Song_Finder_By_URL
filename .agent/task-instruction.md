# Task Instruction — Song Finder

## Task 1: Setup Environment
- [ ] Install Python 3.10+
- [ ] Install `ffmpeg` di sistem (pastikan bisa dipanggil dari command line)
- [ ] Buat virtual environment (`venv`)
- [ ] Install dependencies: `flask`, `yt-dlp`, `pyacoustid`, `python-dotenv`
- [ ] Daftar API key gratis di AcoustID (acoustid.org) dan simpan di file `.env`

## Task 2: Modul Extraction (`extractor/video_extractor.py`)
- [ ] Buat fungsi `extract_audio(url: str) -> str` yang:
  - Validasi URL (cek domain termasuk platform yang didukung)
  - Panggil `yt-dlp` untuk download audio stream dari URL
  - Convert hasil ke format `.wav` menggunakan `ffmpeg`
  - Simpan ke folder `temp/` dengan nama file unik
  - Return path file audio
- [ ] Handle error: URL invalid, video tidak ditemukan, video private

## Task 3: Modul Fingerprinting (`fingerprint/identify.py`)
- [ ] Buat fungsi `identify_song(audio_path: str) -> dict` yang:
  - Generate fingerprint dari file audio (chromaprint)
  - Kirim fingerprint ke AcoustID API
  - Parse response jadi format `{title, artist, score}`
- [ ] Handle error: lagu tidak ditemukan, API timeout/gagal

## Task 4: Backend API (`app.py`)
- [ ] Setup Flask app
- [ ] Buat endpoint `POST /api/identify` yang menghubungkan extraction → fingerprinting → response JSON
- [ ] Tambahkan cleanup otomatis file temp setelah proses selesai
- [ ] Tambahkan error handling sesuai tabel di `design.md`

## Task 5: Frontend (`templates/index.html`, `static/`)
- [ ] Buat form input URL sederhana
- [ ] Tambahkan tombol submit + loading indicator (proses bisa makan beberapa detik)
- [ ] Tampilkan hasil (judul lagu, artis) setelah response diterima
- [ ] Tampilkan pesan error yang jelas kalau gagal

## Task 6: Testing Manual
- [ ] Test dengan URL YouTube Shorts
- [ ] Test dengan URL TikTok
- [ ] Test dengan URL Instagram Reels
- [ ] Test dengan URL invalid (bukan link video)
- [ ] Test dengan video yang lagunya obscure/tidak ada di database (expect: pesan "tidak ditemukan", bukan crash)

## Task 7: Dokumentasi
- [ ] Tulis `README.md` singkat: cara install & jalankan project secara local
- [ ] Cantumkan daftar platform yang didukung beserta batasannya

## Urutan Pengerjaan yang Disarankan
1. Task 1 (setup) → 2. Task 2 (extraction, test manual dulu tanpa fingerprinting) → 3. Task 3 (fingerprinting, test terpisah) → 4. Task 4 (gabungkan jadi API) → 5. Task 5 (frontend) → 6. Task 6 (testing end-to-end) → 7. Task 7 (dokumentasi)
