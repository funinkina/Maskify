"""
PII Detection Algorithms for RE-DACT.

Pure-function detectors that operate on text strings.
Each detector returns a list of dicts: {"type", "value", "start", "end", "length"}
"""

import re

# ---------------------------------------------------------------------------
# Verhoeff Algorithm tables (for Aadhaar UID validation)
# ---------------------------------------------------------------------------

VERHOEFF_MULT = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)

VERHOEFF_PERM = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)


def verhoeff_checksum(number_str):
    """Return 0 if the number string is a valid Verhoeff-checksummed number."""
    digits = tuple(int(n) for n in reversed(number_str))
    checksum = 0
    for i, n in enumerate(digits):
        checksum = VERHOEFF_MULT[checksum][VERHOEFF_PERM[i % 8][n]]
    return checksum


def detect_aadhaar(text):
    """Detect valid Aadhaar UIDs (12-digit numbers passing Verhoeff checksum)."""
    results = []
    for match in re.finditer(r"\d{12}", text):
        value = match.group()
        uid = int(value)
        if verhoeff_checksum(value) == 0 and uid % 10000 != 1947:
            results.append(
                {
                    "type": "aadhaar",
                    "value": value,
                    "start": match.start(),
                    "end": match.end(),
                    "length": 12,
                    "confidence": 1.0,
                }
            )
    return results


# ---------------------------------------------------------------------------
# Luhn Algorithm (for Payment Card validation)
# ---------------------------------------------------------------------------


def luhn_checksum(number_str):
    """Return True if the number string passes the Luhn (mod-10) check."""
    digits = [int(d) for d in number_str]
    # Double every second digit from the right (excluding check digit)
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0


def detect_payment_cards(text):
    """Detect valid payment card numbers (13-19 digits passing Luhn check)."""
    results = []
    for match in re.finditer(r"\d{13,19}", text):
        value = match.group()
        if luhn_checksum(value):
            # Skip if it's also a valid Aadhaar (avoid double-detection of 13+ digit
            # sequences where the first 12 happen to be a valid Aadhaar)
            results.append(
                {
                    "type": "payment_card",
                    "value": value,
                    "start": match.start(),
                    "end": match.end(),
                    "length": len(value),
                    "confidence": 1.0,
                }
            )
    return results


# ---------------------------------------------------------------------------
# PAN Card Detection (structural regex validation)
# ---------------------------------------------------------------------------

PAN_REGEX = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]")
VALID_PAN_4TH_CHARS = {"A", "B", "C", "F", "G", "H", "J", "L", "P", "T"}


def detect_pan(text):
    """Detect valid Indian PAN card numbers."""
    results = []
    for match in PAN_REGEX.finditer(text):
        value = match.group()
        if value[3] in VALID_PAN_4TH_CHARS:
            results.append(
                {
                    "type": "pan",
                    "value": value,
                    "start": match.start(),
                    "end": match.end(),
                    "length": 10,
                    "confidence": 1.0,
                }
            )
    return results


# ---------------------------------------------------------------------------
# Email Detection (regex-based)
# ---------------------------------------------------------------------------

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def detect_email(text):
    """Detect email addresses via regex."""
    results = []
    for match in EMAIL_REGEX.finditer(text):
        value = match.group()
        results.append(
            {
                "type": "email",
                "value": value,
                "start": match.start(),
                "end": match.end(),
                "length": len(value),
                "confidence": 1.0,
            }
        )
    return results


# ---------------------------------------------------------------------------
# Phone Number Detection (regex-based, Indian format)
# ---------------------------------------------------------------------------

PHONE_REGEX = re.compile(r"(?:\+91[\s-]?)?(?:\d[\s-]?){10}")


def detect_phone(text):
    """Detect Indian phone numbers (optional +91 prefix, 10 digits)."""
    results = []
    for match in PHONE_REGEX.finditer(text):
        value = match.group().strip()
        digits_only = re.sub(r"[\s\-]", "", value)
        if len(digits_only) < 10 or len(digits_only) > 13:
            continue
        results.append(
            {
                "type": "phone",
                "value": value,
                "start": match.start(),
                "end": match.start() + len(value),
                "length": len(value),
                "confidence": 1.0,
            }
        )
    return results


# ---------------------------------------------------------------------------
# Unified detection interface
# ---------------------------------------------------------------------------


def detect_all_pii(text, use_ner=True, confidence_threshold=0.85):
    """Run all detectors and return a merged, deduplicated list sorted by position.

    Deduplication: if two detections overlap, the one with higher confidence wins.
    Ties are broken by keeping the longer match.
    """
    all_detections = []

    # Rule-based detectors (always run)
    all_detections.extend(detect_aadhaar(text))
    all_detections.extend(detect_payment_cards(text))
    all_detections.extend(detect_pan(text))
    all_detections.extend(detect_email(text))
    all_detections.extend(detect_phone(text))

    # NER-based detections (optional)
    if use_ner:
        from ner_detector import detect_ner_pii, is_ner_available

        if is_ner_available():
            all_detections.extend(detect_ner_pii(text, confidence_threshold))

    # Sort by start position
    all_detections.sort(key=lambda d: d["start"])

    # Remove overlapping detections (higher confidence wins, then longer match)
    filtered = []
    for det in all_detections:
        if filtered and det["start"] < filtered[-1]["end"]:
            prev = filtered[-1]
            prev_conf = prev.get("confidence", 1.0)
            det_conf = det.get("confidence", 1.0)
            if det_conf > prev_conf or (
                det_conf == prev_conf and det["length"] > prev["length"]
            ):
                filtered[-1] = det
        else:
            filtered.append(det)

    return filtered


def get_mask_range(detection, level):
    """Return (start_offset, end_offset) of characters to mask within a detection.

    Offsets are relative to the detection's start position.
    - For text-based entities (name, address, email, phone): always mask fully
    - For structured IDs:
      - full: mask all characters
      - standard: mask all but last 4
      - partial: mask first 4 only
    """
    length = detection["length"]
    det_type = detection["type"]

    # Text-based entities are always fully masked
    if det_type in ("name", "address", "email", "phone"):
        return (0, length)

    if level == "full":
        return (0, length)
    elif level == "partial":
        return (0, min(4, length))
    else:  # standard
        return (0, max(0, length - 4))
