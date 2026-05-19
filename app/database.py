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


@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    """FastAPI lifespan:啟動時連線,關閉時釋放。"""
    await connect_to_mongo()
    yield
    await close_mongo_connection()
