"""
Tamper-evident audit logging for RE-DACT.

Writes JSON-lines to an audit log file. Each entry includes a SHA-256 hash
of the previous entry, forming a hash chain that detects tampering.
"""

import hashlib
import json
import os
import threading
from datetime import datetime, timezone

AUDIT_LOG_PATH = os.environ.get("AUDIT_LOG_PATH", "./audit.log")

_lock = threading.Lock()
_prev_hash = "0" * 64  # Genesis hash


def _compute_hash(entry_json):
    return hashlib.sha256(entry_json.encode("utf-8")).hexdigest()


def log_redaction(request_id, filename, file_type, level, stats, processing_time_ms):
    """Append a tamper-evident audit log entry."""
    global _prev_hash

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "filename": filename,
        "file_type": file_type,
        "level": level,
        "total_found": stats.get("total_detections", 0),
        "by_type": stats.get("by_type", {}),
        "pages_processed": stats.get("pages_processed", 0),
        "processing_time_ms": processing_time_ms,
        "action": "redacted"
        if stats.get("total_detections", 0) > 0
        else "no_pii_found",
    }

    with _lock:
        entry["prev_hash"] = _prev_hash
        entry_json = json.dumps(entry, separators=(",", ":"), sort_keys=True)
        _prev_hash = _compute_hash(entry_json)
        entry["hash"] = _prev_hash

        with open(AUDIT_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
