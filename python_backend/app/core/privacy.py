import re


_PII_PATTERNS = [
    re.compile(r"\b\d{10,11}\b"),  # phone-like numbers
    re.compile(r"\b\d{11}\b"),  # national-id-like
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),  # email
]


def anonymize_text(text: str) -> str:
    """
    Best-effort masking of obvious PII for logs/analytics.
    Does NOT change the text used for NLP, only for logging.
    """
    if not text:
        return text
    masked = text
    for pattern in _PII_PATTERNS:
        masked = pattern.sub("[PII]", masked)
    return masked

