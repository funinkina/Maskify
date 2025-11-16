# Maskify

A powerful document redaction system that automatically detects and masks Aadhaar UIDs (Unique Identification Numbers) from PDF and image files using OCR and the Verhoeff algorithm for validation.

## 📋 Overview

maskify is an intelligent document processing tool developed for SIH-2024 that helps protect sensitive personal information by automatically detecting and redacting Aadhaar numbers from documents. The system uses advanced OCR technology combined with mathematical validation to ensure accurate identification of genuine UIDs before masking them.

## ✨ Features

- **Automatic UID Detection**: Uses Tesseract OCR to extract text from documents
- **Verhoeff Algorithm Validation**: Validates detected UIDs using the Verhoeff checksum algorithm
- **Multi-Format Support**: Processes both PDF and image files (JPG/JPEG)
- **Smart Rotation Detection**: Automatically detects document orientation
- **Precise Masking**: Redacts UIDs by masking individual digits with black rectangles
- **REST API**: Easy-to-use HTTP endpoint for document processing
- **Docker Support**: Containerized deployment for consistent environments

## 🛠️ Technology Stack

### Backend
- **Node.js** with Express.js - REST API server
- **Python 3.11** - Document processing engine
- **Tesseract OCR** - Optical character recognition
- **OpenCV** - Image processing and manipulation
- **Poppler** - PDF to image conversion

### Key Python Libraries
- `pytesseract` - OCR text extraction
- `opencv-python` - Image processing
- `pdf2image` - PDF conversion
- `img2pdf` - PDF generation
- `pillow` - Image manipulation
- `numpy` - Numerical operations
- `regex` - Pattern matching

## 📦 Installation

### Prerequisites
- Node.js (v18+)
- Python (v3.11+)
- Tesseract OCR
- Poppler utilities

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/funinkina/Maskify.git
   cd Maskify
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install system dependencies**
   
   For Ubuntu/Debian:
   ```bash
   sudo apt-get update
   sudo apt-get install -y tesseract-ocr poppler-utils
   ```
   
   For macOS:
   ```bash
   brew install tesseract poppler
   ```

5. **Create uploads directory**
   ```bash
   mkdir -p uploads
   ```

### Docker Setup

Build and run using Docker:

```bash
docker build -t maskify .
docker run -p 3000:3000 maskify
```

## 🚀 Usage

### Starting the Server

**Development mode:**
```bash
npm run dev
```

**Production mode:**
```bash
npm start
```

The server will start on `http://localhost:3000`

### API Endpoint

**POST** `/process-file`

Upload a document for UID redaction.

**Parameters:**
- `file` (file, required): PDF or JPG/JPEG file to process
- `level` (string, required): Redaction level (currently supports standard redaction)

**Example using cURL:**
```bash
curl -X POST http://localhost:3000/process-file \
  -F "file=@/path/to/document.pdf" \
  -F "level=standard" \
  --output redacted_document.pdf
```

**Example using JavaScript (fetch):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('level', 'standard');

fetch('http://localhost:3000/process-file', {
  method: 'POST',
  body: formData
})
  .then(response => response.blob())
  .then(blob => {
    // Handle the redacted file
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'redacted_document.pdf';
    a.click();
  });
```

**Response:**
- Success: Returns the redacted file (same format as input)
- Error: Returns error message with appropriate HTTP status code

## 🔍 How It Works

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

## 📁 Project Structure

```
Maskify/
├── index.js              # Express server and API endpoints
├── redaction.py          # Python script for UID detection and masking
├── package.json          # Node.js dependencies
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── vercel.json          # Vercel deployment config
├── uploads/             # Temporary file storage
└── Readme.md           # Project documentation
```

## 🔒 Security Considerations

- Temporary files are automatically cleaned up after processing
- Uploaded files are stored temporarily only during processing
- No persistent storage of sensitive documents
- Original files are deleted after redaction

## ⚠️ TODO

- [ ] Currently processes only the first page of multi-page PDFs
- [ ] Optimized for standard Aadhaar card formats
- [ ] Requires clear, readable text for accurate OCR
- [ ] Processing time varies based on image quality and resolution
