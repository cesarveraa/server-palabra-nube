# app/deps.py
from fastapi import Header, HTTPException, Request
from typing import Optional
from app.utils.security import verify_recaptcha

async def captcha_dependency(request: Request, x_captcha_token: Optional[str] = Header(default=None)):
    if request.method == "OPTIONS":  # <- clave
        return
    if not verify_recaptcha(x_captcha_token):
        raise HTTPException(status_code=400, detail="captcha_failed")
