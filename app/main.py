from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.models import JobState
from app.services.cutter_driver import CutterDriver
from app.services.database import JobDatabase
from app.services.device_manager import DeviceManager
from app.services.files import ensure_directories, get_upload_dir, safe_filename
from app.services.job_queue import JobQueue

ensure_directories()

APP_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = str(APP_DIR / "templates")
STATIC_DIR = str(APP_DIR / "static")

app = FastAPI(title="Vinyl Cut Server", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

job_queue = JobQueue(db=JobDatabase())
device_manager = DeviceManager()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/status")
async def status():
    return {
        "app": "vinyl-cut-server",
        "version": "0.1.0",
        "status": "running",
        "device_count": len(device_manager.scan()),
    }


@app.get("/api/devices")
async def devices():
    return {"devices": device_manager.scan()}


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    upload_dir = get_upload_dir()
    filename = safe_filename(file.filename or "upload.svg")
    destination = upload_dir / filename
    with destination.open("wb") as handle:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    return {"filename": filename, "path": str(destination)}


@app.get("/api/jobs")
async def jobs():
    return {"jobs": job_queue.list_jobs()}


@app.post("/api/jobs")
async def create_job(
    filename: str = Form(...),
    device_id: str = Form("simulated-usb-cutter"),
    speed: int = Form(8),
    pressure: int = Form(12),
    tool: str = Form("autoblade"),
):
    job = job_queue.create_job(
        filename=filename,
        device_id=device_id,
        settings={
            "speed": speed,
            "pressure": pressure,
            "tool": tool,
        },
    )
    return {"job": job.to_dict()}


@app.post("/api/jobs/{job_id}/start")
async def start_job(job_id: str):
    job = job_queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status in {JobState.completed, JobState.cancelled, JobState.failed}:
        raise HTTPException(status_code=400, detail="Job cannot be started")

    job.status = JobState.queued
    job_queue.start_job(job_id, CutterDriver(), lambda updated: None)
    return {"job": job.to_dict()}


@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    job = job_queue.cancel_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job": job.to_dict()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({
                "jobs": job_queue.list_jobs(),
                "devices": device_manager.scan(),
            })
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        return


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
