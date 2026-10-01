import os
import shutil
import uuid
import zipfile
import tarfile
import json
import time
import asyncio
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from detector import detect_framework
from generator import generate_stack
from ai_enhancer import enhance_with_ai

app = FastAPI(title="Docker Stack Generator", version="1.0")

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


def cleanup_old_uploads():
    now = time.time()
    for folder in [UPLOAD_DIR, OUTPUT_DIR]:
        for item in folder.iterdir():
            if item.is_dir():
                try:
                    if now - item.stat().st_mtime > 3600:
                        shutil.rmtree(item)
                except Exception:
                    pass


@app.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    cleanup_old_uploads()
    return templates.TemplateResponse(request, "upload.html", {"request": request})


@app.get("/confirm", response_class=HTMLResponse)
async def confirm_page(request: Request):
    return templates.TemplateResponse(request, "confirm.html", {"request": request})


ALLOWED_ARCHIVE_EXTENSIONS = (".zip", ".tar", ".tar.gz", ".tgz")


def _extract_archive(archive_path: Path, dest_dir: Path) -> None:
    name = archive_path.name.lower()
    if name.endswith(".zip"):
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(dest_dir)
    elif name.endswith(".tar.gz") or name.endswith(".tgz"):
        with tarfile.open(archive_path, "r:gz") as tf:
            tf.extractall(dest_dir, filter="data")
    elif name.endswith(".tar"):
        with tarfile.open(archive_path, "r:") as tf:
            tf.extractall(dest_dir, filter="data")
    else:
        raise HTTPException(status_code=400, detail="Unsupported archive type")


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    fname = file.filename or ""
    fname_lower = fname.lower()
    if not fname_lower.endswith(ALLOWED_ARCHIVE_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Only .zip, .tar, .tar.gz files are allowed",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 100MB)")

    session_id = str(uuid.uuid4())[:8]
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    archive_path = session_dir / fname
    with open(archive_path, "wb") as f:
        f.write(content)

    try:
        _extract_archive(archive_path, session_dir)
    except (zipfile.BadZipFile, tarfile.TarError) as e:
        shutil.rmtree(session_dir)
        raise HTTPException(status_code=400, detail=f"Invalid archive file: {e}")

    source_dir = session_dir
    contents = [
        item for item in session_dir.iterdir()
        if item.name.lower() != fname_lower
    ]
    if len(contents) == 1 and contents[0].is_dir():
        source_dir = contents[0]

    detection = detect_framework(str(source_dir))

    return JSONResponse({
        "session_id": session_id,
        "framework": detection["framework"],
        "detected_port": detection["default_port"],
        "db_suggestion": detection["db_suggestion"],
        "type": detection["type"],
        "source_dir": str(source_dir),
    })


@app.post("/generate")
async def generate(
    session_id: str = Form(...),
    app_name: str = Form(...),
    domain: str = Form("localhost"),
    port: int = Form(8080),
    db_type: str = Form("none"),
    enable_sso: bool = Form(False),
    sso_provider: str = Form("keycloak"),
    sso_client_id: str = Form(""),
    sso_client_secret: str = Form(""),
    sso_tenant_id: str = Form(""),
    sso_domain: str = Form(""),
    enable_ai: bool = Form(False),
    ai_provider: str = Form("openai"),
    ai_api_key: str = Form(""),
    framework: str = Form("generic"),
    source_dir: str = Form(""),
):
    session_dir = UPLOAD_DIR / session_id
    if not session_dir.exists():
        raise HTTPException(status_code=400, detail="Session expired or invalid")

    ai_result = None
    if enable_ai and ai_api_key:
        try:
            ai_result = await asyncio.to_thread(
                enhance_with_ai,
                provider=ai_provider,
                api_key=ai_api_key,
                framework=framework,
                source_dir=source_dir,
            )
        except Exception as e:
            ai_result = {"error": str(e)}

    output_dir = OUTPUT_DIR / session_id
    output_dir.mkdir(exist_ok=True)

    generate_stack(
        app_name=app_name,
        domain=domain,
        port=port,
        db_type=db_type,
        enable_sso=enable_sso,
        sso_provider=sso_provider,
        sso_client_id=sso_client_id,
        sso_client_secret=sso_client_secret,
        sso_tenant_id=sso_tenant_id,
        sso_domain=sso_domain,
        framework=framework,
        source_dir=source_dir,
        output_dir=str(output_dir),
        ai_result=ai_result,
    )

    zip_name = f"{app_name}-docker-stack.zip"
    zip_path = output_dir / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file == zip_name:
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(output_dir)
                zf.write(file_path, arcname)

    return JSONResponse({
        "download_url": f"/download/{session_id}/{zip_name}",
        "ai_used": ai_result is not None and "error" not in (ai_result or {}),
        "ai_error": ai_result.get("error") if ai_result and "error" in ai_result else None,
    })


@app.get("/download/{session_id}/{filename}")
async def download(session_id: str, filename: str):
    file_path = OUTPUT_DIR / session_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/zip",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
