"""FastAPI ASGI entrypoint."""

from fastapi import FastAPI

from .api.routes import router

app = FastAPI(
    title="BizMail AI Assistant",
    version="0.1.0",
    docs_url="/api/docs",
)

app.include_router(router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}

