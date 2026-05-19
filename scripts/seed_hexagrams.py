"""
種子腳本:把 64 卦資料寫入 MongoDB。

使用方式:
    python -m scripts.seed_hexagrams         # 預設保留既有資料,只 upsert
    python -m scripts.seed_hexagrams --reset # 先清空 hexagrams collection
"""
import argparse
import asyncio
import sys
from pathlib import Path

# 讓腳本可以從專案根目錄獨立執行
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import connect_to_mongo, close_mongo_connection, get_database  # noqa: E402
from data.hexagrams_seed import build_seed_documents  # noqa: E402


async def main(reset: bool = False) -> None:
    await connect_to_mongo()
    db = get_database()

    if reset:
        await db.hexagrams.delete_many({})
        print("Cleared hexagrams collection.")

    docs = build_seed_documents()
    for doc in docs:
        await db.hexagrams.update_one(
            {"inner": doc["inner"], "outer": doc["outer"]},
            {"$set": doc},
            upsert=True,
        )
    print(f"Seeded {len(docs)} hexagrams.")

    count = await db.hexagrams.count_documents({})
    print(f"Total in DB: {count}")

    await close_mongo_connection()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Drop hexagrams before seeding")
    args = parser.parse_args()
    asyncio.run(main(reset=args.reset))
