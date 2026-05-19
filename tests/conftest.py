"""Pytest shared fixtures。

提供:
- `client`: httpx.AsyncClient 連到 ASGI app,適合做 endpoint 整合測試
- 測試前清空並 seed `zhouyi_test` DB(獨立於 dev/prod)
"""
import os
import sys
from pathlib import Path

# 讓 tests/ 內的測試能 import 專案模組
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


@pytest.fixture(scope="session", autouse=True)
def _use_test_db():
    """整個 session 期間使用獨立 test DB。settings 的 lru_cache 也要清掉。"""
    os.environ["MONGODB_DB"] = "zhouyi_test"
    # 確保有 URI;CI 會設,本地若沒 .env 就用 localhost
    os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27018")
    os.environ.setdefault("CORS_ORIGINS", "*")
    os.environ.setdefault("N8N_AI_WEBHOOK", "")

    from app.config import get_settings
    get_settings.cache_clear()


@pytest_asyncio.fixture
async def client():
    """準備乾淨的 DB + seed + httpx AsyncClient。每個測試一個新 client。"""
    from app.database import connect_to_mongo, close_mongo_connection, get_database
    from app.main import app
    from data.hexagrams_seed import build_seed_documents

    await connect_to_mongo()
    db = get_database()

    # 清乾淨
    await db.divinations.delete_many({})
    await db.hexagrams.delete_many({})

    # Seed 64 卦(同 production auto-seed 邏輯)
    for doc in build_seed_documents():
        await db.hexagrams.update_one(
            {"inner": doc["inner"], "outer": doc["outer"]},
            {"$set": doc},
            upsert=True,
        )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await close_mongo_connection()
