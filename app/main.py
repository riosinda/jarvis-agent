from fastapi import FastAPI

from app.api.routes import router as chat_router

app = FastAPI(title="Jarvis Agent", version="0.1.0")

app.include_router(chat_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
