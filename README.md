# Docker Stack Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/Angga-Permana-Git/docker-generator)

Web application untuk mengotomatisasi pembuatan **Docker stack production-ready** — upload source code (ZIP/TAR), dapatkan Dockerfile + docker-compose + config Apache + SSO + README dalam hitungan detik.

**Fitur utama:**
- **Auto-detect framework** (10 framework: Next.js, React, Node/Express, Laravel, CodeIgniter 3/4, Django, FastAPI, Flask, Generic)
- **Security hardening** (non-root user, read-only FS, resource limits, network segmentation, security headers)
- **Dual mode output** (app-only untuk DB eksternal, fullstack untuk DB lokal)
- **SSO integration** (Keycloak, Auth0, Azure AD, Generic OIDC, Generic OIDC Custom)
- **AI enhancement** (opsional — analisis source code via OpenAI / Anthropic API)
- **Reverse proxy Apache** (SSL, security headers, rate limiting)

---

## Prasyarat

> Contoh perintah di bawah memakai **PowerShell (Windows)**. Untuk **Linux/macOS**: gunakan `python3`/`pip3`, clone ke folder mana saja (mis. `~/projects`), dan perintah shell yang sama.

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
| Git | ✅ Ya | Clone repository |
| Docker Desktop | ❌ Opsional | Testing output stack |
| OpenAI / Anthropic API Key | ❌ Opsional | Fitur AI enhancement |

---

## Instalasi

### 1. Clone repository

Clone ke folder mana saja (di sini contohnya folder home):

```powershell
cd ~
git clone https://github.com/Angga-Permana-Git/docker-generator.git docker-generator
cd docker-generator
```

> **Linux/macOS:**
> ```bash
> cd ~
> git clone https://github.com/Angga-Permana-Git/docker-generator.git docker-generator
> cd docker-generator
> ```

### 2. Install dependency Python

Disarankan memakai **virtual environment** agar dependency tidak bercampur dengan paket sistem:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **Linux/macOS:**
> ```bash
> python3 -m venv venv
> source venv/bin/activate
> pip install -r requirements.txt
> ```

> **Jika aktivasi venv diblokir (Windows):** jalankan dulu
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
> lalu ulangi `.\venv\Scripts\Activate.ps1`.

> **Jika tidak mau pakai venv:** `pip install -r requirements.txt` (atau `pip install --user -r requirements.txt`).

Dependency yang terinstall:
- `fastapi` — web framework
- `uvicorn` — ASGI server
- `python-multipart` — file upload
- `jinja2` — template engine
- `openai` — integrasi AI (opsional)
- `httpx` — HTTP client

### 3. Jalankan aplikasi

Pastikan virtual environment masih aktif (prompt diawali `(venv)`), lalu:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Buka browser: **http://localhost:8000**

> **Tips:** Untuk development dengan auto-reload:
> ```powershell
> python -m uvicorn main:app --reload --port 8000
> ```
>
> **Linux/macOS:** gunakan `python3 -m uvicorn ...` jika perintah `python` tidak dikenali.

---

## Cara Penggunaan

### Langkah 1 — Upload Source Code

1. Buka **http://localhost:8000** di browser
2. Drag & drop atau klik untuk memilih file project dalam format:
   - `.zip`
   - `.tar`
   - `.tar.gz` / `.tgz`
3. Klik **"Detect Framework"**

> **Catatan:** Maksimal 100MB. Jika project punya wrapper folder (misal `myproject/`), sistem otomatis handle. Upload bersifat sementara — **selesaikan proses dalam 1 jam**, sesi lebih tua otomatis dibersihkan.

### Langkah 2 — Konfirmasi & Konfigurasi

Setelah deteksi selesai, halaman konfigurasi menampilkan:

| Field | Keterangan |
|-------|-----------|
| **Framework** | Hasil auto-detect (bisa diubah) |
| **App Name** | Nama aplikasi (untuk container & file) |
| **Domain** | Domain production (mis. `myapp.example.com`) |
| **Port** | Port aplikasi (auto-sesuai framework) |
| **Database Type** | None / PostgreSQL / MySQL / MariaDB |
| **Enable SSO** | Centang + pilih provider (opsional) |
| **Enable AI Analysis** | Centang + pilih provider (OpenAI / Anthropic) + isi API key (opsional) |

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

Ekstrak ZIP, lalu ikuti instruksi lengkap di `README.md` di dalam ZIP tersebut. Ringkasan perintah (jalankan di **Linux server / WSL / Git Bash** — bukan PowerShell, karena perintahnya bergaya Linux):

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
├── ai_enhancer.py        # AI integration (OpenAI / Anthropic)
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
├── LICENSE
├── .gitignore
└── README.md
```

---

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `python` tidak dikenali | Install Python + centang "Add to PATH", atau pakai `python3` |
| `ModuleNotFoundError: No module named 'fastapi'` | Virtual environment belum aktif / belum install dependency — aktifkan `venv` lalu `pip install -r requirements.txt` |
| Aktivasi `venv` diblokir (Windows) | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` lalu aktifkan ulang |
| `pip install` gagal | Cek koneksi internet, coba `pip install --user -r requirements.txt` |
| `error: externally-managed-environment` | Pakai virtual environment (lihat langkah Install dependency) |
| Port 8000 sudah dipakai | Ganti port: `--port 8001` |
| Upload gagal | Pastikan format `.zip`/`.tar`/`.tar.gz`, ukuran < 100MB |
| `Session expired or invalid` | Upload sudah lewat 1 jam — upload ulang file-nya |
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
Perintah di atas hanya memeriksa sintaks seluruh modul (tidak error = OK).

---

## Lisensi

MIT License — silakan digunakan, dimodifikasi, dan didistribusikan secara bebas.
