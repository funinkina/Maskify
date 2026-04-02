# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Maskify** is a document redaction system that detects and masks Aadhaar UIDs from PDF and image files using OCR (Tesseract) and the Verhoeff checksum algorithm for validation. Built for SIH-2024.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Development (auto-reload)
uvicorn app:app --reload

# Production
uvicorn app:app --host 0.0.0.0 --port 8000

# System dependencies (macOS)
brew install tesseract poppler

# Docker
docker build -t maskify . && docker run -p 8000:8000 maskify
```

There is no test suite or linter configured.

## Architecture

Pure Python FastAPI application:

1. **API Layer (`app.py`)** — FastAPI server on port 8000. Single endpoint `POST /process-file` accepts multipart file uploads. Calls the redaction module directly, returns the masked file, then cleans up temp files via a background task.

2. **Redaction Engine (`redaction.py`)** — Core processing pipeline:
   - PDF → 300 DPI images via `pdf2image`/poppler
   - OCR with Tesseract to get text + bounding boxes
   - Regex finds 12-digit sequences, validates with Verhoeff checksum
   - Tests 8 orientations (4 rotations × 2 blur states) for rotated documents
   - Masks each digit individually with black rectangles via OpenCV
   - Converts back to PDF if input was PDF
   - Uses a `work_dir` parameter for per-request file isolation (concurrent-safe)

Key functions: `compute_checksum()` (Verhoeff validation), `Regex_Search()` (pattern detection + filtering), `Extract_and_Mask_UIDs()` (orchestration across rotations), `redact()` (entry point handling format conversion).

## API

`POST /process-file` with multipart form data:
- `file` — PDF or JPG/JPEG
- `level` — Redaction level (currently only 'standard')

Returns the processed file in its original format.

## Deployment

- **Vercel**: Configured in `vercel.json` — uses `@vercel/python` for the FastAPI ASGI app.
- **Docker**: Python 3.11-slim base with Tesseract and Poppler, exposes port 8000.

## Known Limitations

- Only processes the first page of multi-page PDFs
- Optimized for standard Aadhaar card formats only
- Requires clear, readable text for accurate OCR
