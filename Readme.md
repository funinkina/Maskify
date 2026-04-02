# Maskify

A powerful document redaction system that automatically detects and masks Aadhaar UIDs (Unique Identification Numbers) from PDF and image files using OCR and the Verhoeff algorithm for validation.

## Overview

Maskify is an intelligent document processing tool developed for SIH-2024 that helps protect sensitive personal information by automatically detecting and redacting Aadhaar numbers from documents. The system uses advanced OCR technology combined with mathematical validation to ensure accurate identification of genuine UIDs before masking them.

## Features

- **Automatic UID Detection**: Uses Tesseract OCR to extract text from documents
- **Verhoeff Algorithm Validation**: Validates detected UIDs using the Verhoeff checksum algorithm
- **Multi-Format Support**: Processes both PDF and image files (JPG/JPEG)
- **Smart Rotation Detection**: Automatically detects document orientation
- **Precise Masking**: Redacts UIDs by masking individual digits with black rectangles
- **REST API**: Easy-to-use HTTP endpoint for document processing
- **Docker Support**: Containerized deployment for consistent environments

## Technology Stack

- **Python 3.11** with **FastAPI** — REST API server
- **Tesseract OCR** — Optical character recognition
- **OpenCV** — Image processing and manipulation
- **Poppler** — PDF to image conversion

### Key Libraries
- `fastapi` / `uvicorn` — ASGI web framework and server
- `pytesseract` — OCR text extraction
- `opencv-python-headless` — Image processing
- `pdf2image` — PDF conversion
- `img2pdf` — PDF generation
- `pillow` — Image manipulation
- `numpy` — Numerical operations
- `regex` — Pattern matching

## Installation

### Prerequisites
- Python (v3.11+)
- Tesseract OCR
- Poppler utilities

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/funinkina/Maskify.git
   cd Maskify
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install system dependencies**
   
   For Ubuntu/Debian:
   ```bash
   sudo apt-get update
   sudo apt-get install -y tesseract-ocr poppler-utils
   ```
   
   For macOS:
   ```bash
   brew install tesseract poppler
   ```

### Docker Setup

Build and run using Docker:

```bash
docker build -t maskify .
docker run -p 8000:8000 maskify
```

## Usage

### Starting the Server

**Development mode (with auto-reload):**
```bash
uvicorn app:app --reload
```

**Production mode:**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

### API Endpoint

**POST** `/process-file`

Upload a document for UID redaction.

**Parameters:**
- `file` (file, required): PDF or JPG/JPEG file to process
- `level` (string, required): Redaction level (currently supports standard redaction)

**Example using cURL:**
```bash
curl -X POST http://localhost:8000/process-file \
  -F "file=@/path/to/document.pdf" \
  -F "level=standard" \
  --output redacted_document.pdf
```

**Example using Python (requests):**
```python
import requests

with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/process-file",
        files={"file": f},
        data={"level": "standard"},
    )

with open("redacted_document.pdf", "wb") as f:
    f.write(response.content)
```

**Response:**
- Success: Returns the redacted file (same format as input)
- 400: Unsupported file type
- 422: No UIDs found in the document
- 500: Processing error

## How It Works

1. **File Upload**: User uploads a PDF or image file through the API
2. **PDF Conversion**: If PDF, converts first page to high-resolution image (300 DPI)
3. **OCR Processing**: Tesseract extracts text with bounding box coordinates
4. **Pattern Matching**: Regex searches for 12-digit number sequences
5. **UID Validation**: 
   - Applies Verhoeff algorithm to validate checksum
   - Filters out numbers ending in 1947 (Aadhaar year filter)
6. **Rotation Detection**: Tests multiple orientations and blur levels
7. **Redaction**: Masks validated UIDs with black rectangles
8. **Output Generation**: Returns processed file in original format

### Verhoeff Algorithm

The system uses the Verhoeff algorithm to validate Aadhaar numbers. This checksum algorithm is specifically designed to catch common transcription errors and provides a higher level of validation than simpler checksum methods.

## Project Structure

```
Maskify/
├── app.py               # FastAPI server and API endpoint
├── redaction.py          # Python engine for UID detection and masking
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
├── vercel.json           # Vercel deployment config
└── Readme.md             # Project documentation
```

## Security Considerations

- Temporary files are automatically cleaned up after processing
- Each request uses an isolated temp directory (concurrent-safe)
- No persistent storage of sensitive documents

## Known Limitations

- Currently processes only the first page of multi-page PDFs
- Optimized for standard Aadhaar card formats
- Requires clear, readable text for accurate OCR
- Processing time varies based on image quality and resolution
