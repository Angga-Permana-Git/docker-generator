# Docker Stack Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0-blue.svg)]()

Web application untuk mengotomatisasi pembuatan **Docker stack production-ready** — upload source code (ZIP/TAR), dapatkan Dockerfile + docker-compose + config Apache + SSO + README dalam hitungan detik.

**Fitur utama:**
- **Auto-detect framework** (10 framework: Next.js, React, Node/Express, Laravel, CodeIgniter 3/4, Django, FastAPI, Flask, Generic)
- **Security hardening** (non-root user, read-only FS, resource limits, network segmentation, security headers)
- **Dual mode output** (app-only untuk DB eksternal, fullstack untuk DB lokal)
- **SSO integration** (Keycloak, Auth0, Azure AD, Generic OIDC, Generic OIDC Custom)
- **AI enhancement** (opsional — analisis source code via OpenAI API)
- **Reverse proxy Apache** (SSL, security headers, rate limiting)

---

## Prasyarat (Windows)

### 1. Python 3.11 atau lebih baru

Cek apakah sudah terinstall:
```powershell
python --version
```

Jika belum, unduh dari [python.org](https://www.python.org/downloads/) — **centang "Add Python to PATH"** saat instalasi.

### 2. pip (package manager Python)

`pip` ikut terinstall bersama Python. Cek:
```powershell
pip --version
```

### 3. Git (untuk clone repository)

Cek:
```powershell
git --version
```

Jika belum, unduh dari [git-scm.com](https://git-scm.com/download/win).

### 4. Docker Desktop (untuk testing output)

Diperlukan hanya jika ingin **menjalankan/menguji** stack yang di-generate. Untuk sekadar generate file, tidak wajib.

Unduh dari [docker.com](https://www.docker.com/products/docker-desktop/).

### Ringkasan Prasyarat

| Software | Wajib? | Kegunaan |
|----------|--------|----------|
| Python 3.11+ | ✅ Ya | Menjalankan aplikasi |
| pip | ✅ Ya | Install dependency |
| Git | ✅ Ya | Clone & push repository |
| Docker Desktop | ❌ Opsional | Testing output stack |
| OpenAI API Key | ❌ Opsional | Fitur AI enhancement |

---

## Instalasi

### 1. Clone repository

```powershell
cd C:\xampp\htdocs
git clone https://github.com/Angga-Permana-Git/docker-generator.git docker-generator
cd docker-generator
```

### 2. Install dependency Python

```powershell
pip install -r requirements.txt
```

Dependency yang terinstall:
- `fastapi` — web framework
- `uvicorn` — ASGI server
- `python-multipart` — file upload
- `jinja2` — template engine
- `openai` — integrasi AI (opsional)
- `httpx` — HTTP client

### 3. Jalankan aplikasi

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Buka browser: **http://localhost:8000**

> **Tips:** Untuk development dengan auto-reload:
> ```powershell
> python -m uvicorn main:app --reload --port 8000
> ```

---

## Cara Penggunaan

### Langkah 1 — Upload Source Code

1. Buka **http://localhost:8000** di browser
2. Drag & drop atau klik untuk memilih file project dalam format:
   - `.zip`
   - `.tar`
   - `.tar.gz` / `.tgz`
3. Klik **"Detect Framework"**

> **Catatan:** Maksimal 100MB. Jika project punya wrapper folder (misal `myproject/`), sistem otomatis handle.

### Langkah 2 — Konfirmasi & Konfigurasi

Setelah deteksi selesai, halaman konfigurasi menampilkan:

| Field | Keterangan |
|-------|-----------|
| **Framework** | Hasil auto-detect (bisa diubah) |
| **App Name** | Nama aplikasi (untuk container & file) |
| **Domain** | Domain production (mis. `myapp.example.com`) |
| **Port** | Port aplikasi (auto-sesuai framework) |
| **Database** | None / PostgreSQL / MySQL / MariaDB |
| **SSO** | Aktifkan & pilih provider (opsional) |
| **AI Analysis** | Centang + isi OpenAI API Key (opsional) |

**Pilihan SSO Provider:**

| Provider | Cocok untuk |
|----------|------------|
| Keycloak | Self-hosted SSO |
| Auth0 | SaaS Auth0 tenant |
| Azure AD | Microsoft Entra ID |
| Generic OIDC | SSO standar OIDC |
| Generic OIDC (Custom) | IdP eksternal dengan format env custom (`SSO_URL`, `SSO_CLIENT_KEY`, dll) |

### Langkah 3 — Generate & Download

1. Klik **"Generate Stack"**
2. Tunggu proses selesai
3. Klik **"Download ZIP"**

### Langkah 4 — Deploy

Ekstrak ZIP, lalu ikuti instruksi di `README.md` di dalamnya:

```bash
# 1. Buat SSL certificate (development)
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/cert.key -out ssl/cert.crt \
  -subj "/CN=your-domain.example.com"

# 2. Setup environment
cp .env.example.fulldb .env
# Edit .env — isi password, SSO credentials, dll

# 3. Jalankan
docker compose -f docker-compose.fulldb.yaml up -d --build
```

---

## Struktur Output

```
{appname}-dockerstack/
├── Dockerfile                    # Multi-stage, hardened
├── docker-compose.app.yaml       # Mode: app + proxy (DB eksternal)
├── docker-compose.fulldb.yaml    # Mode: app + proxy + DB (lokal)
├── .env.example.app              # Template env (mode app)
├── .env.example.fulldb           # Template env (mode fulldb)
├── .dockerignore                 # .env TIDAK di-bake ke image
├── .gitignore
├── apache/
│   ├── app.conf.template         # Reverse proxy + SSL + security headers
│   └── entrypoint.sh             # Apache startup script
├── ssl/                          # (buat sendiri) sertifikat SSL
├── README.md                     # Instruksi deploy lengkap
└── aianalysis.md                 # (jika AI aktif) Hasil analisis
```

---

## Struktur Aplikasi (Source Code)

```
docker-generator/
├── main.py               # FastAPI routing & upload handler
├── detector.py           # Framework detection logic
├── generator.py          # Stack generation & ZIP creation
├── ai_enhancer.py        # OpenAI integration
├── security_hardener.py  # SSO configuration
├── templates/
│   ├── upload.html       # Halaman upload
│   ├── confirm.html      # Form konfigurasi
│   ├── dockercompose.app.j2
│   ├── dockercompose.fulldb.j2
│   ├── env.app.j2 / env.fulldb.j2
│   ├── README.j2 / aianalysis.j2
│   ├── dockerfile/       # 10 template Dockerfile
│   └── apache/           # Reverse proxy templates
├── static/               # CSS & JavaScript
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `python` tidak dikenali | Install Python + centang "Add to PATH" |
| `pip install` gagal | Cek koneksi internet, coba `pip install --user -r requirements.txt` |
| Port 8000 sudah dipakai | Ganti port: `--port 8001` |
| Upload gagal | Pastikan format `.zip`/`.tar`/`.tar.gz`, ukuran < 100MB |
| Framework terdeteksi salah | Bisa diubah manual di halaman konfigurasi |
| AI tidak jalan | Cek API key, atau matikan centang AI (tetap generate normal) |

---

## Development

### Menjalankan dalam mode dev
```powershell
python -m uvicorn main:app --reload --port 8000
```

### Testing
```powershell
python -m py_compile main.py detector.py generator.py ai_enhancer.py security_hardener.py
```

---

## Lisensi

MIT License — silakan digunakan, dimodifikasi, dan didistribusikan secara bebas.
