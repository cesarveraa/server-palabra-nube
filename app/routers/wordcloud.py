# app/routers/wordcloud.py
from fastapi import APIRouter, Depends, Header
from fastapi import Response
from typing import Optional
from app.models.schemas import WordcloudResponse
from app.services.firestore_client import get_db
from app.services.word_service import fetch_wordcloud

router = APIRouter(prefix="/api", tags=["wordcloud"])
@router.get("/wordcloud", response_model=WordcloudResponse, responses={304: {"description": "Not Modified"}})
async def wordcloud(
    limit: int = 200,
    if_none_match: Optional[str] = Header(default=None, alias="If-None-Match"),
    resp: Response = None,
    db = Depends(get_db),
):
    data = fetch_wordcloud(db, limit=limit)
    etag = f"\"v{data['version']}\""

    if if_none_match == etag:
        return Response(status_code=304, headers={"ETag": etag})

    # añadir ETag en 200 OK
    resp.headers["ETag"] = etag
    return data
