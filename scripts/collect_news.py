"""
뉴스 수집 스크립트.

실행: python scripts/collect_news.py
권장 주기: 3시간 (하루 8회)

수집 흐름:
  1. GDELT (무제한, API 키 불필요) → 이벤트 감지 + 지리 좌표
  2. 중복 제거 + 중요도 산정
  3. 기사 URL에서 리드 문단(300자) 추출 → 분류 정확도 향상
  4. gpt-4o-mini로 한국어 번역 + 카테고리 재분류 (배치)
  5. MongoDB upsert (url 기준 중복 방지)
  6. 30일 초과 기사 자동 만료 (TTL 인덱스)
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser

import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

from app.services.news_sources import (
    GdeltSource,
    NewsDataSource,
    GNewsSource,
    QuotaExhausted,
    CATEGORY_KEYWORDS,
    PIN_COLORS,
    _pin_size,
)

CATEGORIES = list(CATEGORY_KEYWORDS.keys())

PRIMARY = GdeltSource()
FALLBACK_CHAIN = [NewsDataSource(), GNewsSource()]


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
    """중요도 산정 (기본 2, 향후 확장 가능)."""
    for a in articles:
        a["importance"] = 2
        a["pin_size"] = _pin_size(a["importance"])
        a.pop("_source_count", None)
        a.pop("_origin", None)
    return articles


async def collect_category(category: str, client: httpx.AsyncClient) -> list[dict]:
    all_articles = []

    try:
        articles = await PRIMARY.fetch(category, client)
        all_articles.extend(articles)
        print(f"  [GDELT] {category}: {len(articles)}건")
    except Exception as e:
        print(f"  [GDELT] {category}: 실패 - {e}")

    if not all_articles:
        for source in FALLBACK_CHAIN:
            try:
                articles = await source.fetch(category, client)
                all_articles.extend(articles)
                print(f"  [{source.name}] {category}: {len(articles)}건")
                break
            except QuotaExhausted:
                print(f"  [{source.name}] {category}: 할당량 소진 → 다음 소스로 폴백")
            except Exception as e:
                print(f"  [{source.name}] {category}: 실패 ({e}) → 다음 소스로 폴백")

    return all_articles


SNIPPET_MAX_CHARS = 300
SNIPPET_CONCURRENCY = 5
SNIPPET_TIMEOUT = 5


class _ParagraphExtractor(HTMLParser):
    """<p> 태그 안의 텍스트만 추출하는 경량 HTML 파서."""

    def __init__(self):
        super().__init__()
        self._in_p = False
        self._skip = 0
        self._skip_tags = frozenset({"script", "style", "nav", "header", "footer", "aside"})
        self.paragraphs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self._skip_tags:
            self._skip += 1
        elif tag == "p" and self._skip == 0:
            self._in_p = True

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._skip = max(0, self._skip - 1)
        elif tag == "p":
            self._in_p = False

    def handle_data(self, data):
        if self._in_p and self._skip == 0:
            text = data.strip()
            if text:
                self.paragraphs.append(text)


def _extract_text(html: str, max_chars: int = SNIPPET_MAX_CHARS) -> str:
    """HTML에서 meta description 또는 <p> 태그 텍스트를 추출."""
    for pattern in (
        r'<meta\s+(?:name="description"|property="og:description")\s+content="([^"]*)"',
        r'<meta\s+content="([^"]*)"\s+(?:name="description"|property="og:description")',
    ):
        m = re.search(pattern, html[:5000], re.IGNORECASE)
        if m and len(m.group(1).strip()) > 50:
            return m.group(1).strip()[:max_chars]

    parser = _ParagraphExtractor()
    try:
        parser.feed(html)
    except Exception:
        return ""
    full = " ".join(parser.paragraphs)
    return full[:max_chars]


async def _fetch_one_snippet(url: str, client: httpx.AsyncClient,
                             sem: asyncio.Semaphore) -> str:
    async with sem:
        try:
            resp = await client.get(url, timeout=SNIPPET_TIMEOUT, follow_redirects=True)
            if resp.status_code != 200:
                return ""
            return _extract_text(resp.text)
        except Exception:
            return ""


async def fetch_snippets(articles: list[dict]) -> list[dict]:
    """summary가 비어 있는 기사의 URL에서 리드 문단을 가져와 summary에 저장."""
    targets = [(i, a["url"]) for i, a in enumerate(articles)
               if not a.get("summary") and a.get("url")]

    if not targets:
        print("[본문] 추출 불필요 (모든 기사에 요약 있음)")
        return articles

    sem = asyncio.Semaphore(SNIPPET_CONCURRENCY)
    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
        tasks = [_fetch_one_snippet(url, client, sem) for _, url in targets]
        results = await asyncio.gather(*tasks)

    filled = 0
    for (idx, _), text in zip(targets, results):
        if text:
            articles[idx]["summary"] = text
            filled += 1

    print(f"[본문] {filled}/{len(targets)}건 리드 문단 추출 완료")
    return articles


TRANSLATE_PROMPT = """다음 뉴스 기사들에 대해 두 가지 작업을 수행하세요:

1. 제목(title)과 요약(summary)을 자연스러운 한국어로 번역하세요.
   - 번역만 하고 내용을 추가하거나 변경하지 마세요.
   - summary가 빈 문자열이면 빈 문자열로 유지하세요.

2. 제목과 요약을 종합적으로 분석하여 아래 5개 카테고리 중 가장 적합한 하나를 선택하세요:
   - war: 실제 군사 교전, 전투 행위, 군사 작전 수행, 무력 공격, 폭격, 포격, 미사일 발사 등 직접적 무력 충돌
     ※ 주의: 개인적 총격 사건, 강도, 살인, 폭행 등 일반 범죄는 war가 아닙니다.
     ※ 주의: UN 결의안, 평화 협상, 휴전 협정, 외교적 성명, 제재 결의, 국제기구 대응 등은 전쟁 관련 맥락이더라도 politics로 분류하세요.
   - economy: 경제, 무역, 금융, 주식, 환율, 물가, 기업 실적, 관세, 경기침체, 유가, 에너지 시장
   - disaster: 자연재해, 기후, 환경 오염, 전염병, 대형 사고
   - politics: 정치, 외교, 선거, 정상회담, 제재, 법안, 정부 정책, UN/국제기구 결의, 외교적 대응, 평화 협상
   - others: 위 4개에 해당하지 않는 기사 (범죄, 사건사고, 연예, 스포츠, 라이프스타일 등)

※ 분류 시 제목뿐 아니라 summary(기사 본문 발췌)의 내용을 반드시 함께 고려하세요.
※ 전쟁 중 발생한 사건이라도, 기사의 주제가 외교·정치적 대응이면 politics, 경제적 영향이면 economy로 분류하세요.

반드시 아래 JSON 형식으로만 응답하세요:
{"translations": [{"idx": 0, "title": "한국어 제목", "summary": "한국어 요약", "category": "war"}, ...]}"""

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
            items.append({
                "idx": i,
                "title": a["title"],
                "summary": a.get("summary", ""),
                "original_category": a.get("category", ""),
            })

        try:
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": TRANSLATE_PROMPT},
                    {"role": "user", "content": json.dumps(items, ensure_ascii=False)},
                ],
                temperature=0.3,
                max_tokens=4000,
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

            valid_categories = {"war", "economy", "disaster", "politics", "others"}
            for item in items_list:
                idx = item.get("idx", -1)
                if 0 <= idx < len(batch):
                    batch[idx]["title_en"] = batch[idx]["title"]
                    batch[idx]["summary_en"] = batch[idx].get("summary", "")
                    batch[idx]["title"] = item["title"]
                    batch[idx]["summary"] = item.get("summary", "")
                    new_cat = item.get("category", "")
                    if new_cat in valid_categories:
                        batch[idx]["category"] = new_cat
                        batch[idx]["pin_color"] = PIN_COLORS.get(new_cat, "#94a3b8")
                    translated += 1

        except Exception as e:
            print(f"  [번역] 배치 실패 ({start}~{start+len(batch)-1}): {e}")

        if start + BATCH_SIZE < len(articles):
            await asyncio.sleep(1)

    reclassified = sum(1 for a in articles if a.get("category") == "others")
    print(f"[번역] {translated}/{len(articles)}건 한국어 번역 완료")
    print(f"[분류] others로 재분류: {reclassified}건")
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


async def main(db=None):
    print(f"=== 뉴스 수집 시작 ({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}) ===")

    own_client = None
    if db is None:
        own_client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
        db = own_client[os.getenv("MONGODB_DB_NAME")]

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

    existing_urls = set()
    urls_to_check = [a["url"] for a in unique if a.get("url")]
    if urls_to_check:
        cursor = db.news.find({"url": {"$in": urls_to_check}}, {"url": 1, "_id": 0})
        async for doc in cursor:
            existing_urls.add(doc["url"])

    new_articles = [a for a in unique if a["url"] not in existing_urls]
    print(f"DB 미존재 신규 기사: {len(new_articles)}건 (기존 {len(existing_urls)}건 스킵)")

    scored = calc_importance(new_articles)

    print("\n기사 본문 추출 중...")
    await fetch_snippets(scored)

    print("\n한국어 번역 중...")
    translated = await translate_articles(scored)

    saved, skipped = await save_to_db(translated, db)

    print(f"DB 저장: {saved}건 신규, {skipped}건 이미 존재")

    total = await db.news.count_documents({})
    print(f"DB 전체 뉴스: {total}건")
    print("=== 수집 완료 ===")

    if own_client:
        own_client.close()


if __name__ == "__main__":
    asyncio.run(main())
