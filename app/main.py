"""FastAPI 主程式入口。"""
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import lifespan
from app.routers import ai, divinate, hexagrams, history

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("zhouyi")

settings = get_settings()

app = FastAPI(
    title="蓍草法周易占卜 API",
    description="Refactored zhouyi service — FastAPI + MongoDB",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(divinate.router)
app.include_router(hexagrams.router)
app.include_router(history.router)
app.include_router(ai.router)


@app.get("/health", tags=["meta"])
async def health() -> dict:
    """Render health check endpoint。"""
    return {"status": "ok", "service": "zhouyi", "version": "2.0.0"}


# 靜態前端 — 將 /static 掛載,並讓根目錄回傳 index.html
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    @app.get("/{lang}", include_in_schema=False)
    async def index(lang: str = "zh-TW"):
        # 前端 SPA 自己處理 lang 路由,後端只負責回傳 index.html
        if lang not in ("zh-TW", "en"):
            # 不是支援的語言,可能是其他前端路由,還是回 index.html
            pass
        return FileResponse(STATIC_DIR / "index.html")
