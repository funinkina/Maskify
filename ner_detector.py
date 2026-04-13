"""
NER-based PII detection for RE-DACT.

Uses a pre-trained BERT NER model from Hugging Face to detect
unstructured PII (names, addresses) that cannot be caught by
rule-based detectors.

Falls back gracefully if transformers/torch are not installed.
"""

_ner_pipeline = None
_ner_available = None

# Map NER labels to RE-DACT PII types
NER_LABEL_MAP = {
    "PER": "name",
    "LOC": "address",
}

DEFAULT_MODEL = "dslim/bert-base-NER"
DEFAULT_CONFIDENCE_THRESHOLD = 0.85


def is_ner_available():
    """Check if transformers and torch are installed."""
    global _ner_available
    if _ner_available is None:
        try:
            import transformers  # noqa: F401
            import torch  # noqa: F401
            _ner_available = True
        except ImportError:
            _ner_available = False
    return _ner_available


def _get_pipeline():
    """Lazy-load the NER pipeline singleton."""
    global _ner_pipeline
    if _ner_pipeline is None:
        from transformers import pipeline
        _ner_pipeline = pipeline(
            "ner",
            model=DEFAULT_MODEL,
            aggregation_strategy="simple",
        )
    return _ner_pipeline


def detect_ner_pii(text, confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD):
    """Run NER on text and return detections in the standard format.

    Each detection is a dict with keys:
        type, value, start, end, length, confidence

    Returns an empty list if transformers is not installed.
    """
    if not is_ner_available():
        return []

    pipe = _get_pipeline()

    # BERT models have a max token limit (~512 tokens).
    # For long OCR text, process in chunks to avoid truncation.
    results = []
    chunk_size = 512
    overlap = 50

    if len(text) <= chunk_size:
        chunks = [(0, text)]
    else:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append((start, text[start:end]))
            if end >= len(text):
                break
            start = end - overlap

    seen_spans = set()

    for offset, chunk in chunks:
        try:
            raw_entities = pipe(chunk)
        except Exception:
            continue

        for entity in raw_entities:
            label = entity["entity_group"]
            if label not in NER_LABEL_MAP:
                continue
            if entity["score"] < confidence_threshold:
                continue

            abs_start = offset + entity["start"]
            abs_end = offset + entity["end"]
            span_key = (abs_start, abs_end)

            if span_key in seen_spans:
                continue
            seen_spans.add(span_key)

            value = text[abs_start:abs_end]

            results.append({
                "type": NER_LABEL_MAP[label],
                "value": value,
                "start": abs_start,
                "end": abs_end,
                "length": abs_end - abs_start,
                "confidence": round(entity["score"], 4),
            })

    return results
