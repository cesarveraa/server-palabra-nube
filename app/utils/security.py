import hmac, hashlib, requests
from typing import Optional
from app.config import settings

def hmac_hash_ip_fp(ip: str, fp: str = "") -> str:
    msg = f"{ip}|{fp}".encode("utf-8")
    key = settings.HASH_SECRET.encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()[:32]

def get_client_ip(x_forwarded_for: Optional[str], fallback_ip: str) -> str:
    if x_forwarded_for:
        # Puede llegar "ip1, ip2, ip3"
        return x_forwarded_for.split(",")[0].strip()
    return (fallback_ip or "").strip()

def verify_recaptcha(token: Optional[str]) -> bool:
    if not settings.REQUIRE_CAPTCHA:
        return True
    if not token or not settings.RECAPTCHA_SECRET:
        return False
    # Google reCAPTCHA v3 endpoint; para Turnstile cambia la URL y campos
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {"secret": settings.RECAPTCHA_SECRET, "response": token}
    try:
        r = requests.post(url, data=data, timeout=3)
        ok = r.ok and r.json().get("success", False)
        return bool(ok)
    except Exception:
        return False
