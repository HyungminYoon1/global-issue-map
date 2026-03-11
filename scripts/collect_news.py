"""
뉴스 수집 스크립트.

실행: python scripts/collect_news.py
권장 주기: 6시간 (하루 4회)

수집 흐름:
  1. GDELT (1차, 무제한) → 이벤트 감지 + 지리 좌표
  2. NewsData.io → GNews → Currents API (2차 체인, 할당량 소진 시 폴백)
  3. 중복 제거 + 교차검증 기반 중요도 산정
  4. gpt-4o-mini로 제목+요약 한국어 번역 (배치)
  5. MongoDB upsert (url 기준 중복 방지)
  6. 30일 초과 기사 자동 만료 (TTL 인덱스)
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone

import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

from app.services.news_sources import (
    GdeltSource,
    NewsDataSource,
    GNewsSource,
    CurrentsSource,
    QuotaExhausted,
    CATEGORY_KEYWORDS,
    PIN_COLORS,
    _pin_size,
)

CATEGORIES = list(CATEGORY_KEYWORDS.keys())

PRIMARY = GdeltSource()
SECONDARY_CHAIN = [NewsDataSource(), GNewsSource(), CurrentsSource()]


def _title_words(title: str) -> set:
    return set(title.lower().split())


def deduplicate(articles: list[dict]) -> list[dict]:
    """제목 단어 유사도 60% 이상이면 동일 기사로 판단. 출처 수가 많은 쪽을 우선."""
    unique = []
    for article in articles:
        words = _title_words(article["title"])
        merged = False
        for existing in unique:
            ex_words = _title_words(existing["title"])
            if not words or not ex_words:
                continue
            overlap = len(words & ex_words) / min(len(words), len(ex_words))
            if overlap > 0.6:
                existing["_source_count"] = existing.get("_source_count", 1) + 1
                if not existing.get("summary") and article.get("summary"):
                    existing["summary"] = article["summary"]
                merged = True
                break
        if not merged:
            article["_source_count"] = 1
            unique.append(article)
    return unique


def calc_importance(articles: list[dict]) -> list[dict]:
    """교차검증: 복수 소스에서 감지된 기사는 중요도 상향."""
    for a in articles:
        base = 2
        source_bonus = min(a.get("_source_count", 1) - 1, 2)
        a["importance"] = min(base + source_bonus, 5)
        a["pin_size"] = _pin_size(a["importance"])
        a.pop("_source_count", None)
        a.pop("_origin", None)
    return articles


async def collect_category(category: str, client: httpx.AsyncClient) -> list[dict]:
    all_articles = []

    # 1차: GDELT (무제한)
    try:
        gdelt_articles = await PRIMARY.fetch(category, client)
        all_articles.extend(gdelt_articles)
        print(f"  [GDELT] {category}: {len(gdelt_articles)}건")
    except Exception as e:
        print(f"  [GDELT] {category}: 실패 - {e}")

    # 2차: 폴백 체인 (첫 번째 성공 소스만 사용)
    for source in SECONDARY_CHAIN:
        try:
            secondary_articles = await source.fetch(category, client)
            all_articles.extend(secondary_articles)
            print(f"  [{source.name}] {category}: {len(secondary_articles)}건")
            break
        except QuotaExhausted as e:
            print(f"  [{source.name}] {category}: 할당량 소진 → 다음 소스로 폴백")
            continue
        except Exception as e:
            print(f"  [{source.name}] {category}: 실패 ({e}) → 다음 소스로 폴백")
            continue

    return all_articles


TRANSLATE_PROMPT = """다음 뉴스 기사들의 제목(title)과 요약(summary)을 자연스러운 한국어로 번역하세요.
번역만 하고 내용을 추가하거나 변경하지 마세요.
summary가 빈 문자열이면 빈 문자열로 유지하세요.

반드시 아래 JSON 형식으로만 응답하세요:
{"translations": [{"idx": 0, "title": "한국어 제목", "summary": "한국어 요약"}, ...]}"""

BATCH_SIZE = 10


async def translate_articles(articles: list[dict]) -> list[dict]:
    """gpt-4o-mini로 제목+요약을 한국어 번역 (배치 처리)."""
    from openai import AsyncOpenAI
    from app.config import settings

    if not settings.openai_api_key:
        print("[번역] OpenAI API 키 없음 - 원문 유지")
        return articles

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    translated = 0

    for start in range(0, len(articles), BATCH_SIZE):
        batch = articles[start:start + BATCH_SIZE]

        items = []
        for i, a in enumerate(batch):
            items.append({"idx": i, "title": a["title"], "summary": a.get("summary", "")})

        try:
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": TRANSLATE_PROMPT},
                    {"role": "user", "content": json.dumps(items, ensure_ascii=False)},
                ],
                temperature=0.3,
                max_tokens=3000,
                response_format={"type": "json_object"},
            )

            content = resp.choices[0].message.content
            result = json.loads(content)

            items_list = []
            if isinstance(result, list):
                items_list = result
            elif isinstance(result, dict):
                items_list = result.get("translations", [])
                if not items_list:
                    for v in result.values():
                        if isinstance(v, list):
                            items_list = v
                            break

            for item in items_list:
                idx = item.get("idx", -1)
                if 0 <= idx < len(batch):
                    batch[idx]["title_en"] = batch[idx]["title"]
                    batch[idx]["summary_en"] = batch[idx].get("summary", "")
                    batch[idx]["title"] = item["title"]
                    batch[idx]["summary"] = item.get("summary", "")
                    translated += 1

        except Exception as e:
            print(f"  [번역] 배치 실패 ({start}~{start+len(batch)-1}): {e}")

        if start + BATCH_SIZE < len(articles):
            await asyncio.sleep(1)

    print(f"[번역] {translated}/{len(articles)}건 한국어 번역 완료")
    return articles


async def save_to_db(articles: list[dict], db):
    now = datetime.now(timezone.utc)
    saved = 0
    skipped = 0

    for a in articles:
        a["created_at"] = now
        result = await db.news.update_one(
            {"url": a["url"]},
            {"$setOnInsert": a},
            upsert=True,
        )
        if result.upserted_id:
            saved += 1
        else:
            skipped += 1

    return saved, skipped


async def ensure_indexes(db):
    await db.news.create_index("url", unique=True)
    await db.news.create_index("created_at", expireAfterSeconds=30 * 24 * 60 * 60)
    await db.news.create_index([("category", 1)])
    await db.news.create_index([("continent", 1)])
    await db.news.create_index([("importance", -1)])
    await db.news.create_index([("published_at", -1)])


async def main():
    print(f"=== 뉴스 수집 시작 ({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}) ===")

    client_db = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client_db[os.getenv("MONGODB_DB_NAME")]
    await ensure_indexes(db)

    all_articles = []

    async with httpx.AsyncClient() as http:
        for i, category in enumerate(CATEGORIES):
            if i > 0:
                await asyncio.sleep(10)
            print(f"\n[{category}] 수집 중...")
            articles = await collect_category(category, http)
            all_articles.extend(articles)

    print(f"\n수집 완료: 총 {len(all_articles)}건 (중복 제거 전)")

    unique = deduplicate(all_articles)
    print(f"중복 제거 후: {len(unique)}건")

    scored = calc_importance(unique)

    print("\n한국어 번역 중...")
    translated = await translate_articles(scored)

    saved, skipped = await save_to_db(translated, db)

    print(f"DB 저장: {saved}건 신규, {skipped}건 이미 존재")

    total = await db.news.count_documents({})
    print(f"DB 전체 뉴스: {total}건")
    print("=== 수집 완료 ===")

    client_db.close()


if __name__ == "__main__":
    asyncio.run(main())
