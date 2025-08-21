from pydantic import BaseModel, Field
from typing import Optional, List

class SubmitRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=120)
    fp: Optional[str] = Field(default=None, description="Browser fingerprint")
    captcha_token: Optional[str] = None

class SubmitResponse(BaseModel):
    ok: bool
    lemma: Optional[str] = None
    error: Optional[str] = None

class WordItem(BaseModel):
    text: str
    count: int

class WordcloudResponse(BaseModel):
    version: int
    updatedAt: Optional[str]
    items: List[WordItem]
