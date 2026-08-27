# PRD — Song Finder (Web Pencari Lagu dari URL Video)

## 1. Latar Belakang
Banyak orang nemu video reels/short video (TikTok, IG Reels, YouTube Shorts, dll) dengan lagu yang catchy tapi gak tau judul & artisnya. Web ini menyelesaikan masalah itu: user tinggal paste URL video, sistem akan extract audio dari video tersebut dan mengidentifikasi lagunya.

## 2. Tujuan
- User bisa mengetahui judul, artis, dan info lagu dari sebuah video hanya dengan menempel URL-nya.
- Mendukung berbagai platform video yang punya fitur reels/short video dengan musik.

## 3. Target User
Pengguna umum yang sering nonton reels/short video dan penasaran dengan lagu latar/background music-nya.

## 4. Scope Platform
**Didukung penuh (Tier 1):**
- YouTube (termasuk Shorts)
- TikTok
- Instagram (Reels & feed video)
- Facebook (Reels & video)

**Didukung dengan catatan (Tier 2 — rawan rate limit/block):**
- Twitter/X
- Pinterest
- Snapchat (Spotlight)
- Likee

**Di luar scope (Tier 3 — private/expired content):**
- Instagram Stories
- Snapchat Stories
- WhatsApp Status

## 5. Fitur Utama (Functional Requirements)
| ID | Fitur | Deskripsi |
|----|-------|-----------|
| F1 | Input URL | User paste URL video ke form input |
| F2 | Validasi URL | Sistem cek apakah URL valid & platform didukung |
| F3 | Extract Audio | Sistem download & convert audio dari video (via yt-dlp + ffmpeg) |
| F4 | Identifikasi Lagu | Audio dikirim ke API fingerprinting untuk dapat judul, artis, dll |
| F5 | Tampilkan Hasil | Judul lagu, artis, dan (jika tersedia) link ke Spotify/YouTube Music |
| F6 | Error Handling | Pesan jelas kalau URL invalid, platform gak didukung, atau lagu gak teridentifikasi |

## 6. Non-Functional Requirements
- **Performa**: proses dari input URL sampai hasil idealnya < 15 detik untuk video pendek (<3 menit)
- **Stateless**: tidak ada penyimpanan data permanen (tanpa database) — sesuai keputusan project
- **Environment**: dijalankan secara local (localhost) untuk development & demo
- **Ketergantungan internet**: dibutuhkan koneksi internet aktif karena proses fingerprinting memanggil API eksternal

## 7. Out of Scope
- User account / login
- History pencarian
- Download/simpan file audio untuk didengarkan ulang
- Dukungan penuh untuk konten privat/story yang expired

## 8. Batasan & Risiko
- Beberapa platform (IG, Twitter/X) bisa membatasi/block scraping via `yt-dlp` sewaktu-waktu
- API fingerprinting gratis (AcoustID) punya keterbatasan database dibanding layanan berbayar (ACRCloud/Audd.io)
- Tidak semua lagu di database fingerprinting API — kemungkinan "lagu tidak ditemukan" untuk lagu obscure/remix

## 9. Success Criteria
- Berhasil mengidentifikasi lagu dengan benar untuk mayoritas video dari platform Tier 1
- Sistem berjalan stabil secara local tanpa error fatal untuk kasus penggunaan normal
