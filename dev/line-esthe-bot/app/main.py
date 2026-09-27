from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import init_db
from app.line.webhook import router as line_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="LINE Esthe Review Bot", lifespan=lifespan)
app.include_router(line_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
