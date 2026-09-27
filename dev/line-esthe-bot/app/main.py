from fastapi import FastAPI

from app.line.webhook import router as line_router

app = FastAPI(title="LINE Esthe Review Bot")
app.include_router(line_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
