"""MongoDB 非同步連線。透過 FastAPI lifespan 管理生命週期。"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    """建立 MongoDB 連線並建立必要索引。"""
    global _client, _db
    settings = get_settings()
    logger.info("Connecting to MongoDB...")
    _client = AsyncIOMotorClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )
    # 透過 ping 確認連線可用
    await _client.admin.command("ping")
    _db = _client[settings.mongodb_db]

    # 建立索引(只做一次,MongoDB 會忽略重複定義)
    await _db.hexagrams.create_index([("inner", 1), ("outer", 1)], unique=True)
    await _db.hexagrams.create_index([("sequence", 1)])
    await _db.divinations.create_index([("created_at", -1)])
    await _db.divinations.create_index([("session_id", 1), ("created_at", -1)])

    logger.info("MongoDB connected: db=%s", settings.mongodb_db)


async def close_mongo_connection() -> None:
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """供 router 使用的 DB 取得函式。"""
    if _db is None:
        raise RuntimeError("MongoDB not initialized. Call connect_to_mongo() first.")
    return _db


async def ensure_hexagrams_seeded() -> None:
    """空 collection 時自動灌入 64 卦資料。Render free plan 沒 Shell 可手動跑 script,
    這個 hook 確保部署即可用。Idempotent — 已有資料就跳過。"""
    db = get_database()
    count = await db.hexagrams.count_documents({})
    if count >= 64:
        logger.info("Hexagrams already seeded (%d docs), skip auto-seed", count)
        return

    # 延遲 import 避開循環依賴
    from data.hexagrams_seed import build_seed_documents

    docs = build_seed_documents()
    for doc in docs:
        await db.hexagrams.update_one(
            {"inner": doc["inner"], "outer": doc["outer"]},
            {"$set": doc},
            upsert=True,
        )
    logger.info("Auto-seeded %d hexagrams on startup", len(docs))


@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    """FastAPI lifespan:啟動時連線 + 自動 seed,關閉時釋放。"""
    await connect_to_mongo()
    await ensure_hexagrams_seeded()
    yield
    await close_mongo_connection()
