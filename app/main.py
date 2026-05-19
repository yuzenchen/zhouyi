"""FastAPI 主程式入口。"""
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


# 靜態前端 — 掛載在 root,html=True 自動服務 index.html。
# index.html 用相對路徑(css/main.css 而非 /static/css/main.css),這樣本地單一部署與
# GitHub Pages 子路徑部署 (/zhouyi/) 都能正常解析。
# /static/* 也保留 alias,讓既有書籤或外部連結不會斷。
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static-legacy")
    # 必須最後掛載,否則會吃掉 /api/* 路由
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
