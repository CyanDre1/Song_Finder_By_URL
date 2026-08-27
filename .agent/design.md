# Design Document — Song Finder

## 1. Tech Stack
| Komponen | Pilihan | Alasan |
|----------|---------|--------|
| Backend | Flask (Python) | Ringan, gampang setup local, cocok untuk API sederhana |
| Video/Audio Extraction | `yt-dlp` | Support ratusan platform video, aktif di-maintain |
| Audio Conversion | `ffmpeg` | Standar industri untuk convert video→audio |
| Audio Fingerprinting | AcoustID (via `pyacoustid` + `chromaprint`) | Gratis, open-source, database dari MusicBrainz |
| Frontend | HTML + CSS + Vanilla JS | Tanpa build tools, cukup untuk scope project |
| Database | — (tidak dipakai, sesuai keputusan) | Project bersifat stateless |

> **Catatan:** Flask & AcoustID dipilih sebagai default. Kalau butuh akurasi lebih tinggi, AcoustID bisa diganti ke ACRCloud/Audd.io tanpa ubah arsitektur besar — cukup ganti modul fingerprinting.

## 2. Arsitektur Alur (High-Level Flow)
```
[Frontend: Form Input URL]
        |
        v
[Backend: POST /api/identify]
        |
        v
[Validasi URL & Platform]
        |
        v
[yt-dlp: Download video/audio stream]
        |
        v
[ffmpeg: Convert ke format audio (WAV/MP3)]
        |
        v
[Generate fingerprint (chromaprint)]
        |
        v
[Kirim fingerprint ke AcoustID API]
        |
        v
[Terima hasil: judul, artis, link]
        |
        v
[Backend: Response JSON]
        |
        v
[Frontend: Tampilkan hasil ke user]
```

## 3. Struktur Folder
```
song-finder/
├── app.py                  # Entry point Flask
├── extractor/
│   └── video_extractor.py  # Wrapper yt-dlp + ffmpeg
├── fingerprint/
│   └── identify.py         # Wrapper AcoustID
├── static/
│   ├── style.css
│   └── script.js
├── templates/
│   └── index.html
├── temp/                   # Folder sementara file audio (auto-cleanup)
├── requirements.txt
└── .env                    # API key AcoustID
```

## 4. API Endpoint

### `POST /api/identify`
**Request body:**
```json
{
  "url": "https://www.tiktok.com/@user/video/xxxx"
}
```

**Response sukses (200):**
```json
{
  "status": "success",
  "song": {
    "title": "Judul Lagu",
    "artist": "Nama Artis",
    "score": 0.95
  }
}
```

**Response gagal (400/404):**
```json
{
  "status": "error",
  "message": "Lagu tidak dapat diidentifikasi"
}
```

## 5. Error Handling
| Kasus | Response |
|-------|----------|
| URL tidak valid / platform tidak didukung | 400 — "Platform tidak didukung" |
| Video tidak bisa diakses (private/expired) | 400 — "Video tidak dapat diakses" |
| Gagal extract audio | 500 — "Gagal memproses video" |
| Lagu tidak ditemukan di database fingerprinting | 404 — "Lagu tidak ditemukan" |
| API fingerprinting error/timeout | 503 — "Layanan identifikasi sedang bermasalah" |

## 6. File Sementara (Temp Handling)
- Audio hasil extract disimpan sementara di folder `temp/`
- Dihapus otomatis setelah proses fingerprinting selesai (baik sukses maupun gagal) untuk menghindari penumpukan file

## 7. Deployment (Local)
- Dijalankan via `python app.py` di localhost (default port 5000)
- Untuk demo ke pihak lain tanpa deploy: gunakan `ngrok` untuk expose localhost ke URL publik sementara
