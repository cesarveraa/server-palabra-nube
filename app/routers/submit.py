from fastapi import APIRouter, Depends, Header, Request, HTTPException
from app.models.schemas import SubmitRequest, SubmitResponse
from app.services.firestore_client import get_db
from app.services.word_service import submit_phrase
from app.utils.security import get_client_ip
from app.deps import captcha_dependency
from typing import Optional
router = APIRouter(prefix="/api", tags=["submit"])

@router.post("/submit", response_model=SubmitResponse)
async def submit(
    payload: SubmitRequest,
    request: Request,
    db = Depends(get_db),
    _ = Depends(captcha_dependency),  # valida si REQUIRE_CAPTCHA=True
    x_forwarded_for:  Optional[str]  = Header(default=None),
    x_fp: Optional[str] = Header(default=None)
):
    # IP real
    client_ip = get_client_ip(x_forwarded_for, request.client.host if request.client else "")
    try:
        lemma, _ = submit_phrase(db, payload.text, client_ip, payload.fp or x_fp)
        return SubmitResponse(ok=True, lemma=lemma)
    except PermissionError as e:
        code = 409 if "already_submitted_today" in str(e) else 429
        raise HTTPException(status_code=code, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail="server_error")
