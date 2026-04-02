import os
import shutil
import tempfile
import uuid

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask

from redaction import redact

app = FastAPI(title="Maskify", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/process-file")
async def process_file(
    file: UploadFile = File(...),
    level: str = Form(...),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".jpg", ".jpeg"):
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, JPG, or JPEG.")

    work_dir = tempfile.mkdtemp(prefix="maskify_")

    try:
        input_path = os.path.join(work_dir, f"{uuid.uuid4().hex}{ext}")
        with open(input_path, "wb") as f:
            f.write(await file.read())

        output_path = redact(input_path, level, work_dir)

        if output_path is None:
            shutil.rmtree(work_dir, ignore_errors=True)
            raise HTTPException(status_code=422, detail="No UIDs found in the document.")

        media_type = "application/pdf" if output_path.endswith(".pdf") else "image/jpeg"

        return FileResponse(
            path=output_path,
            media_type=media_type,
            filename=f"redacted{os.path.splitext(output_path)[1]}",
            background=BackgroundTask(shutil.rmtree, work_dir, True),
        )
    except HTTPException:
        raise
    except Exception as e:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")
