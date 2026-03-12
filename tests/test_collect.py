"""
수집 테스트 스크립트.

각 카테고리별 1건씩만 수집하여 DB에 저장하고,
1분 간격으로 3회 반복하여 신규 기사 추가 여부를 확인한다.

실행: python tests/test_collect.py
"""

import asyncio
import os
import sys
from datetime import datetime, timezone

import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

from scripts.collect_news import (
    collect_category,
    deduplicate,
    calc_importance,
    translate_articles,
    save_to_db,
    ensure_indexes,
    CATEGORIES,
)

TEST_ROUNDS = 3
INTERVAL_SEC = 60


async def test_round(round_num: int, db):
    print(f"\n{'='*60}")
    print(f"[Round {round_num}/{TEST_ROUNDS}] {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
    print(f"{'='*60}")

    all_articles = []

    async with httpx.AsyncClient() as http:
        for i, category in enumerate(CATEGORIES):
            if i > 0:
                await asyncio.sleep(5)
            print(f"\n[{category}] 수집 중...")
            articles = await collect_category(category, http)
            if articles:
                all_articles.append(articles[0])
                print(f"  -> 1건 선택: {articles[0]['title'][:50]}...")
            else:
                print(f"  -> 0건 (수집 실패)")

    print(f"\n수집: {len(all_articles)}건 (카테고리당 1건)")

    unique = deduplicate(all_articles)

    existing_urls = set()
    urls_to_check = [a["url"] for a in unique if a.get("url")]
    if urls_to_check:
        cursor = db.news.find({"url": {"$in": urls_to_check}}, {"url": 1, "_id": 0})
        async for doc in cursor:
            existing_urls.add(doc["url"])

    new_articles = [a for a in unique if a["url"] not in existing_urls]
    print(f"신규: {len(new_articles)}건 / 기존: {len(existing_urls)}건 스킵")

    if not new_articles:
        print("-> 신규 기사 없음, 번역 스킵")
        return

    scored = calc_importance(new_articles)
    translated = await translate_articles(scored)
    saved, skipped = await save_to_db(translated, db)

    print(f"\nDB 저장: {saved}건 신규, {skipped}건 이미 존재")

    for a in translated:
        print(f"  [{a.get('category', '?'):>10}] {a['title'][:50]}")

    total = await db.news.count_documents({})
    print(f"DB 전체: {total}건")


async def main():
    print(f"=== 수집 테스트 시작 ===")
    print(f"설정: 카테고리당 1건, {INTERVAL_SEC}초 간격, {TEST_ROUNDS}회 반복")

    client_db = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client_db[os.getenv("MONGODB_DB_NAME")]
    await ensure_indexes(db)

    before = await db.news.count_documents({})
    print(f"테스트 전 DB 기사 수: {before}건")

    for i in range(1, TEST_ROUNDS + 1):
        await test_round(i, db)
        if i < TEST_ROUNDS:
            print(f"\n다음 라운드까지 {INTERVAL_SEC}초 대기...")
            await asyncio.sleep(INTERVAL_SEC)

    after = await db.news.count_documents({})
    print(f"\n{'='*60}")
    print(f"=== 테스트 완료 ===")
    print(f"테스트 전: {before}건 -> 테스트 후: {after}건 (+{after - before}건)")
    print(f"{'='*60}")

    client_db.close()


if __name__ == "__main__":
    asyncio.run(main())
