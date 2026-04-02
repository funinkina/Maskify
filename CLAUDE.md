# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**RE-DACT** is an AI-driven document redaction platform that detects and masks sensitive PII (Aadhaar UIDs, PAN cards, payment card numbers) from PDF and image files using OCR (Tesseract), checksum validation (Verhoeff, Luhn), and regex-based pattern matching.

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
```

There is no test suite or linter configured.

## Architecture

Pure Python FastAPI application with an HTML frontend:

1. **PII Detectors (`detectors.py`)** — Pure-function detection algorithms:
   - Aadhaar UID: 12-digit Verhoeff checksum validation
   - PAN Card: Regex `[A-Z]{5}[0-9]{4}[A-Z]` with 4th-character entity type validation
   - Payment Card: 13-19 digit Luhn (mod-10) checksum validation
   - Unified `detect_all_pii()` interface with overlap deduplication
   - `get_mask_range()` computes which characters to mask per level

2. **Redaction Engine (`redaction.py`)** — Core processing pipeline:
   - PDF → 300 DPI images via `pdf2image`/poppler (all pages)
   - OCR with Tesseract to get text + bounding boxes
   - Calls `detect_all_pii()` for multi-type PII detection
   - Tests 8 orientations (4 rotations x 2 blur states) for rotated documents
   - Masks characters based on redaction level (standard/partial/full)
   - Combines all pages back into PDF if input was PDF
   - Returns (output_path, stats_dict) with detection statistics

3. **API Layer (`app.py`)** — FastAPI server on port 8000:
   - `POST /api/process-file` — accepts multipart upload, returns JSON with stats + download URL
   - `GET /api/result/{request_id}` — returns the redacted file
   - `GET /api/health` — health check
   - In-memory result store with 10-min TTL
   - Serves static frontend from `static/`

4. **Audit Logger (`audit.py`)** — Tamper-evident JSON-lines logging with SHA-256 hash chain.

5. **Frontend (`static/`)** — Vanilla HTML/CSS/JS single-page app with drag-drop upload, level selection, stats display, and file preview/download.

## API

`POST /api/process-file` with multipart form data:
- `file` — PDF, JPG, JPEG, or PNG
- `level` — Redaction level: `standard` (default), `partial`, or `full`

Returns JSON:
```json
{
    "request_id": "...",
    "stats": {"total_detections": 2, "by_type": {...}, "pages_processed": 1, "detections": [...]},
    "download_url": "/api/result/{request_id}",
    "processing_time_ms": 1234
}
```

`GET /api/result/{request_id}` — returns the redacted file as a download.

## Known Limitations

- Requires clear, readable text for accurate OCR
- PAN detection requires uppercase OCR output
