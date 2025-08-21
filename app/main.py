# app/main.py
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import submit, wordcloud

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    # Permite todo en dev. En prod, usa tu dominio exacto.
    allow_origins = ["*"] if settings.APP_ENV != "prod" else [str(o) for o in settings.ALLOWED_ORIGINS]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=False,       # si lo pones True, no puedes usar "*"
        allow_methods=["*"],           # incluye OPTIONS/POST/GET/...
        allow_headers=["*"],           # permite content-type, x-fp, etc.
        expose_headers=["ETag"],       # para que el front lea el ETag
        max_age=86400,
    )

    # Respuesta 200 para cualquier preflight (por si algún dep corta OPTIONS)
    async def _options_ok(path: str):
        return Response(status_code=200)
    app.add_api_route("/{path:path}", _options_ok, methods=["OPTIONS"])

    app.include_router(submit.router, prefix="")     # deja tu prefijo actual
    app.include_router(wordcloud.router, prefix="")
    return app

app = create_app()
