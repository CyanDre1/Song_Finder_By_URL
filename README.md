# Song Finder

Cari judul dan artis lagu dari URL video. Tempel link YouTube, TikTok, Instagram, atau platform lainnya — dapatkan hasilnya dalam hitungan detik.

## Fitur

- Identifikasi lagu dari video YouTube, TikTok, Instagram, Facebook, X/Twitter, Pinterest, Snapchat, dan Likee
- Tiga layanan fingerprint: AcoustID (primer) → ACRCloud → AudD (fallback otomatis)
- UI modern dengan animasi floating notes
- Error handling dalam Bahasa Indonesia

## Persyaratan

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) — harus bisa dipanggil dari command line (`ffmpeg` di PATH)
- [chromaprint fpcalc](https://acoustid.org/chromaprint) — binary untuk generate audio fingerprint

## Instalasi

```bash
# 1. Buat virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Buat file .env (lihat bagian API Keys)
touch .env
```

### API Keys

Buat file `.env` di root project:

```env
ACOUSTID_API_KEY=your_key_here       # dari https://acoustid.org/new-application

# Opsional — untuk fallback ACRCloud dan AudD
ACRCLOUD_HOST=identify-ap-southeast-1.acrcloud.com
ACRCLOUD_ACCESS_KEY=your_key
ACRCLOUD_ACCESS_SECRET=your_secret

AUDD_API_TOKEN=your_token            # dari https://audd.io
```

Minimal `ACOUSTID_API_KEY` harus diisi. Tanpa key lain, hanya AcoustID yang akan digunakan.

## Menjalankan

```bash
python app.py
```

Buka `http://127.0.0.1:5000` di browser.

## API

```
POST /api/identify
Content-Type: application/json

{ "url": "https://www.youtube.com/watch?v=..." }
```

**Response sukses (200):**
```json
{ "status": "success", "song": { "title": "...", "artist": "...", "score": 0.95 } }
```

**Error codes:**

| HTTP | Kondisi |
|------|---------|
| 400 | URL invalid / platform tidak didukung |
| 400 | Video privat / expired / tidak tersedia |
| 404 | Lagu tidak ditemukan di semua backend |
| 500 | Gagal download atau convert audio |
| 503 | Layanan identifikasi bermasalah |

## Stack

- **Backend:** Flask, yt-dlp, ffmpeg, pyacoustid
- **Frontend:** HTML, CSS (vanilla), JavaScript (vanilla)
- **Fingerprint:** AcoustID → ACRCloud → AudD

## Lisensi

MIT
