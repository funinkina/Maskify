import os
import shutil
import tempfile
import time
import uuid
import threading
from dataclasses import dataclass, field

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from redaction import redact
from audit import log_redaction

app = FastAPI(title="RE-DACT", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory result store with TTL cleanup
# ---------------------------------------------------------------------------

RESULT_TTL_SECONDS = 600  # 10 minutes


@dataclass
class ResultEntry:
    output_path: str
    media_type: str
    work_dir: str
    created_at: float = field(default_factory=time.time)


_results: dict[str, ResultEntry] = {}
_results_lock = threading.Lock()


def _cleanup_expired():
    now = time.time()
    with _results_lock:
        expired = [
            k for k, v in _results.items() if now - v.created_at > RESULT_TTL_SECONDS
        ]
        for key in expired:
            entry = _results.pop(key)
            shutil.rmtree(entry.work_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

MEDIA_TYPES = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "3.0.0"}


@app.post("/api/process-file")
async def process_file(
    file: UploadFile = File(...),
    level: str = Form("standard"),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail="Unsupported file type. Use PDF, JPG, JPEG, or PNG."
        )

    if level not in ("standard", "partial", "full"):
        raise HTTPException(
            status_code=400,
            detail="Invalid redaction level. Use 'standard', 'partial', or 'full'.",
        )

    work_dir = tempfile.mkdtemp(prefix="redact_")
    request_id = uuid.uuid4().hex
    start_time = time.time()

    try:
        input_path = os.path.join(work_dir, f"{request_id}{ext}")
        with open(input_path, "wb") as f:
            f.write(await file.read())

        output_path, stats = redact(input_path, level, work_dir)

        processing_time_ms = int((time.time() - start_time) * 1000)

        # Audit log
        log_redaction(
            request_id, file.filename, ext.lstrip("."), level, stats, processing_time_ms
        )

        if output_path is None:
            shutil.rmtree(work_dir, ignore_errors=True)
            return JSONResponse(
                content={
                    "request_id": request_id,
                    "stats": stats,
                    "download_url": None,
                    "message": "No PII found in the document.",
                },
                status_code=200,
            )

        # Determine media type from output
        out_ext = os.path.splitext(output_path)[1].lower()
        media_type = MEDIA_TYPES.get(out_ext, "application/octet-stream")

        # Store result for download
        with _results_lock:
            _results[request_id] = ResultEntry(
                output_path=output_path,
                media_type=media_type,
                work_dir=work_dir,
            )

        # Trigger cleanup of old results
        _cleanup_expired()

        return JSONResponse(
            content={
                "request_id": request_id,
                "stats": stats,
                "download_url": f"/api/result/{request_id}",
                "processing_time_ms": processing_time_ms,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")


@app.get("/api/result/{request_id}")
async def get_result(request_id: str):
    with _results_lock:
        entry = _results.get(request_id)

    if entry is None:
        raise HTTPException(status_code=404, detail="Result not found or expired.")

    if not os.path.exists(entry.output_path):
        raise HTTPException(status_code=404, detail="Result file no longer available.")

    out_ext = os.path.splitext(entry.output_path)[1]
    return FileResponse(
        path=entry.output_path,
        media_type=entry.media_type,
        filename=f"redacted{out_ext}",
    )


# ---------------------------------------------------------------------------
# Serve frontend (must be last so it doesn't shadow API routes)
# ---------------------------------------------------------------------------

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
