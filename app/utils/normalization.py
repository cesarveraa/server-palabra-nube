import unicodedata, re
from app.config import settings

_token_re = re.compile(r"[a-z0-9ñáéíóúü-]+", re.IGNORECASE)

def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def normalize_phrase(raw: str) -> str:
    s = (raw or "").strip().lower()
    s = strip_accents(s)
    # Solo letras/nums/guión/espacio
    s = re.sub(r"[^a-z0-9 ñáéíóúü-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) < settings.MIN_LEN or len(s) > settings.MAX_LEN:
        raise ValueError("invalid_length")
    # máx tokens
    tokens = _token_re.findall(s)
    if len(tokens) < 1 or len(tokens) > settings.MAX_TOKENS_PER_PHRASE:
        raise ValueError("invalid_tokens")
    return s
