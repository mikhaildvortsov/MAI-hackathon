"""FastAPI ASGI entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from .api.routes import router

app = FastAPI(
    title="BizMail AI Assistant",
    version="0.1.0",
    docs_url="/api/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {"service": "BizMail AI Assistant", "status": "ok", "docs": "/api/docs"}


@app.get("/favicon.ico", tags=["meta"])
async def favicon() -> Response:
    return Response(status_code=204)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}

