const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const clearFile = document.getElementById("clearFile");
const processBtn = document.getElementById("processBtn");
const resultsSection = document.getElementById("resultsSection");
const loadingOverlay = document.getElementById("loadingOverlay");
const errorMessage = document.getElementById("errorMessage");

let selectedFile = null;

// --- File selection ---

dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  if (e.dataTransfer.files.length) {
    setFile(e.dataTransfer.files[0]);
  }
});

fileInput.addEventListener("change", () => {
  if (fileInput.files.length) {
    setFile(fileInput.files[0]);
  }
});

clearFile.addEventListener("click", () => {
  selectedFile = null;
  fileInput.value = "";
  fileInfo.hidden = true;
  dropZone.hidden = false;
  processBtn.disabled = true;
  hideError();
});

function setFile(file) {
  const allowed = [".pdf", ".jpg", ".jpeg", ".png"];
  const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
  if (!allowed.includes(ext)) {
    showError("Unsupported file type. Use PDF, JPG, JPEG, or PNG.");
    return;
  }
  selectedFile = file;
  fileName.textContent = file.name;
  fileSize.textContent = formatFileSize(file.size);
  fileInfo.hidden = false;
  dropZone.hidden = true;
  processBtn.disabled = false;
  hideError();
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

// --- Error handling ---

function showError(msg) {
  errorMessage.textContent = "[ERROR] " + msg;
  errorMessage.hidden = false;
}

function hideError() {
  errorMessage.hidden = true;
}

// --- Process ---

processBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  const level = document.querySelector('input[name="level"]:checked').value;

  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("level", level);

  loadingOverlay.classList.add("active");
  resultsSection.hidden = true;
  hideError();

  try {
    const resp = await fetch("/api/process-file", {
      method: "POST",
      body: formData,
    });

    const data = await resp.json();

    if (!resp.ok) {
      throw new Error(data.detail || "Processing failed");
    }

    displayResults(data, level);
  } catch (err) {
    showError(err.message);
  } finally {
    loadingOverlay.classList.remove("active");
  }
});

// --- Display results ---

function displayResults(data, level) {
  const stats = data.stats || {};
  const total = stats.total_detections || 0;
  const byType = stats.by_type || {};

  // Hero
  document.getElementById("statTotal").textContent = total;

  // Status
  const statusEl = document.getElementById("resultsStatus");
  if (total > 0) {
    statusEl.textContent = "[" + total + " FOUND]";
    statusEl.style.color = "var(--accent)";
  } else {
    statusEl.textContent = "[CLEAN]";
    statusEl.style.color = "var(--success)";
  }

  // Stats row
  document.getElementById("statPages").textContent = stats.pages_processed || 0;
  document.getElementById("statTime").textContent = data.processing_time_ms || 0;
  document.getElementById("statLevel").textContent = level.toUpperCase();

  const ext = selectedFile.name.substring(selectedFile.name.lastIndexOf(".") + 1).toUpperCase();
  document.getElementById("statFileType").textContent = ext;

  // Breakdown bars
  const breakdownSection = document.getElementById("breakdownSection");
  const breakdownItems = document.getElementById("breakdownItems");
  breakdownItems.innerHTML = "";

  const types = [
    { key: "aadhaar", label: "Aadhaar UID", color: "accent" },
    { key: "pan", label: "PAN Card", color: "warning" },
    { key: "payment_card", label: "Payment Card", color: "interactive" },
  ];

  const maxCount = Math.max(total, 1);
  let hasAny = false;

  for (const t of types) {
    const count = byType[t.key] || 0;
    if (count > 0) hasAny = true;

    const item = document.createElement("div");
    item.className = "breakdown-item";

    const header = document.createElement("div");
    header.className = "breakdown-item-header";
    header.innerHTML =
      '<span class="breakdown-item-label">' + escapeHtml(t.label) + "</span>" +
      '<span class="breakdown-item-value">' + count + "</span>";
    item.appendChild(header);

    // Segmented bar: 10 segments
    const segments = 10;
    const filled = total > 0 ? Math.round((count / maxCount) * segments) : 0;
    const bar = document.createElement("div");
    bar.className = "seg-bar";
    for (let i = 0; i < segments; i++) {
      const seg = document.createElement("div");
      seg.className = i < filled ? "seg-bar-fill " + t.color : "seg-bar-empty";
      bar.appendChild(seg);
    }
    item.appendChild(bar);
    breakdownItems.appendChild(item);
  }

  breakdownSection.style.display = hasAny || total > 0 ? "" : "none";

  // Detections table
  const detections = stats.detections || [];
  const tbody = document.getElementById("detectionsBody");
  const detectionsSection = document.getElementById("detectionsSection");
  tbody.innerHTML = "";

  if (detections.length > 0) {
    detectionsSection.hidden = false;
    for (const det of detections) {
      const tr = document.createElement("tr");
      const typeClass = det.type || "";
      tr.innerHTML =
        '<td><span class="detection-type-tag ' + escapeHtml(typeClass) + '">' + escapeHtml(formatType(det.type)) + "</span></td>" +
        "<td>" + escapeHtml(det.masked_value) + "</td>" +
        "<td>" + det.page + "</td>";
      tbody.appendChild(tr);
    }
  } else {
    detectionsSection.hidden = true;
  }

  // No PII message
  const noPiiMessage = document.getElementById("noPiiMessage");
  if (total === 0) {
    noPiiMessage.hidden = false;
  } else {
    noPiiMessage.hidden = true;
  }

  // Preview & Download
  const previewSection = document.getElementById("previewSection");
  const previewContainer = document.getElementById("previewContainer");
  const downloadBtn = document.getElementById("downloadBtn");

  previewContainer.innerHTML = "";

  if (data.download_url) {
    previewSection.hidden = false;
    downloadBtn.href = data.download_url;

    const fileExt = selectedFile.name.substring(selectedFile.name.lastIndexOf(".")).toLowerCase();

    if (fileExt === ".pdf") {
      const iframe = document.createElement("iframe");
      iframe.src = data.download_url;
      previewContainer.appendChild(iframe);
      downloadBtn.download = "redacted.pdf";
    } else {
      const img = document.createElement("img");
      img.src = data.download_url;
      img.alt = "Redacted document";
      previewContainer.appendChild(img);
      downloadBtn.download = "redacted" + fileExt;
    }
  } else {
    previewSection.hidden = true;
  }

  resultsSection.hidden = false;
}

function formatType(type) {
  const labels = {
    aadhaar: "Aadhaar",
    pan: "PAN",
    payment_card: "Card",
  };
  return labels[type] || type;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
