"""뉴스 소스 API 구현. 할당량 소진 시 다음 소스로 자동 폴백."""

import logging
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.geo import lookup_country

logger = logging.getLogger(__name__)

PIN_COLORS = {"war": "#EF4444", "economy": "#16A34A", "politics": "#EAB308", "disaster": "#F97316"}

CATEGORY_KEYWORDS = {
    "war": {
        "gdelt": "war OR conflict OR military OR attack OR troops OR missile",
        "search": "war military conflict",
        "newsdata": "politics",
    },
    "economy": {
        "gdelt": "economy OR trade OR inflation OR GDP OR market OR tariff OR recession",
        "search": "economy trade market",
        "newsdata": "business",
    },
    "disaster": {
        "gdelt": "earthquake OR flood OR hurricane OR wildfire OR tsunami OR cyclone",
        "search": "natural disaster earthquake flood",
        "newsdata": "environment",
    },
    "politics": {
        "gdelt": "election OR president OR parliament OR diplomacy OR summit OR sanctions",
        "search": "politics election diplomacy",
        "newsdata": "politics",
    },
}


def _pin_size(importance: int) -> str:
    if importance >= 5:
        return "large"
    return "medium" if importance >= 3 else "small"


def _normalize(title: str, source: str, summary: str, country: str,
               category: str, published_at: str, url: str, origin: str) -> dict | None:
    geo = lookup_country(country)
    if not geo:
        return None

    return {
        "title": title.strip(),
        "source": source,
        "published_at": published_at,
        "summary": summary[:500] if summary else "",
        "country": country,
        "continent": geo["continent"],
        "region": geo["region"],
        "category": category,
        "keywords": [],
        "lat": geo["lat"],
        "lng": geo["lng"],
        "importance": 1,
        "pin_size": "small",
        "pin_color": PIN_COLORS.get(category, "#94a3b8"),
        "url": url,
        "_origin": origin,
    }


class QuotaExhausted(Exception):
    pass


def _valid_key(key: str) -> bool:
    return bool(key) and "your-" not in key and key != ""


# ──────────────────────────────────────────
# 1차 소스: GDELT (무제한, API 키 불필요)
# ──────────────────────────────────────────
class GdeltSource:
    name = "GDELT"
    BASE = "https://api.gdeltproject.org/api/v2/doc/doc"

    async def fetch(self, category: str, client: httpx.AsyncClient) -> list[dict]:
        import asyncio
        kw = CATEGORY_KEYWORDS[category]
        params = {
            "query": kw["gdelt"],
            "mode": "artlist",
            "maxrecords": "20",
            "format": "json",
            "timespan": "24h",
            "sourcelang": "english",
        }

        for attempt in range(3):
            resp = await client.get(self.BASE, params=params, timeout=15)
            if resp.status_code == 429:
                await asyncio.sleep(10 * (attempt + 1))
                continue
            resp.raise_for_status()
            break
        else:
            raise Exception("GDELT rate limit - 재시도 초과")

        try:
            data = resp.json()
        except Exception:
            return []
        articles = data.get("articles", [])

        results = []
        for a in articles:
            n = _normalize(
                title=a.get("title", ""),
                source=a.get("domain", ""),
                summary="",
                country=a.get("sourcecountry", ""),
                category=category,
                published_at=_parse_gdelt_date(a.get("seendate", "")),
                url=a.get("url", ""),
                origin="gdelt",
            )
            if n:
                results.append(n)
        return results


def _parse_gdelt_date(s: str) -> str:
    try:
        return datetime.strptime(s, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).isoformat()
    except (ValueError, TypeError):
        return datetime.now(timezone.utc).isoformat()


# ──────────────────────────────────────────
# 2차 소스 체인 (할당량 소진 시 순차 폴백)
# ──────────────────────────────────────────
class NewsDataSource:
    name = "NewsData.io"
    BASE = "https://newsdata.io/api/1/news"

    async def fetch(self, category: str, client: httpx.AsyncClient) -> list[dict]:
        key = settings.newsdata_api_key
        if not _valid_key(key):
            raise QuotaExhausted("API key not configured")

        kw = CATEGORY_KEYWORDS[category]
        params = {
            "apikey": key,
            "category": kw["newsdata"],
            "language": "en",
            "size": 10,
        }
        resp = await client.get(self.BASE, params=params, timeout=15)
        if resp.status_code == 429:
            raise QuotaExhausted("NewsData.io quota exceeded")
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "success":
            raise QuotaExhausted(data.get("results", {}).get("message", "API error"))

        results = []
        for a in data.get("results", []) or []:
            country = ""
            if a.get("country"):
                country = a["country"][0] if isinstance(a["country"], list) else a["country"]

            n = _normalize(
                title=a.get("title", ""),
                source=a.get("source_name", a.get("source_id", "")),
                summary=a.get("description", "") or "",
                country=country.title() if country else "",
                category=category,
                published_at=a.get("pubDate", ""),
                url=a.get("link", ""),
                origin="newsdata",
            )
            if n:
                results.append(n)
        return results


class GNewsSource:
    name = "GNews"
    BASE = "https://gnews.io/api/v4/search"

    async def fetch(self, category: str, client: httpx.AsyncClient) -> list[dict]:
        key = settings.gnews_api_key
        if not _valid_key(key):
            raise QuotaExhausted("API key not configured")

        kw = CATEGORY_KEYWORDS[category]
        params = {
            "q": kw["search"],
            "token": key,
            "lang": "en",
            "max": 10,
            "sortby": "publishedAt",
        }
        resp = await client.get(self.BASE, params=params, timeout=15)
        if resp.status_code == 429 or resp.status_code == 403:
            raise QuotaExhausted("GNews quota exceeded")
        resp.raise_for_status()
        data = resp.json()

        results = []
        for a in data.get("articles", []):
            n = _normalize(
                title=a.get("title", ""),
                source=a.get("source", {}).get("name", ""),
                summary=a.get("description", "") or "",
                country=_guess_country_from_source(a.get("source", {}).get("url", "")),
                category=category,
                published_at=a.get("publishedAt", ""),
                url=a.get("url", ""),
                origin="gnews",
            )
            if n:
                results.append(n)
        return results


class CurrentsSource:
    name = "Currents API"
    BASE = "https://api.currentsapi.services/v1/search"

    async def fetch(self, category: str, client: httpx.AsyncClient) -> list[dict]:
        key = settings.currents_api_key
        if not _valid_key(key):
            raise QuotaExhausted("API key not configured")

        kw = CATEGORY_KEYWORDS[category]
        params = {
            "keywords": kw["search"],
            "apiKey": key,
            "language": "en",
            "page_size": 10,
        }
        resp = await client.get(self.BASE, params=params, timeout=15)
        if resp.status_code == 429:
            raise QuotaExhausted("Currents API quota exceeded")
        resp.raise_for_status()
        data = resp.json()

        results = []
        for a in data.get("news", []):
            n = _normalize(
                title=a.get("title", ""),
                source=a.get("author", ""),
                summary=a.get("description", "") or "",
                country="",
                category=category,
                published_at=a.get("published", ""),
                url=a.get("url", ""),
                origin="currents",
            )
            if n:
                results.append(n)
        return results


# GNews는 국가 정보를 직접 제공하지 않으므로 source URL 도메인에서 추정
_DOMAIN_COUNTRY = {
    "reuters.com": "United States", "bbc.co.uk": "United Kingdom", "bbc.com": "United Kingdom",
    "cnn.com": "United States", "aljazeera.com": "United Arab Emirates",
    "theguardian.com": "United Kingdom", "nytimes.com": "United States",
    "washingtonpost.com": "United States", "bloomberg.com": "United States",
    "france24.com": "France", "dw.com": "Germany",
}


def _guess_country_from_source(source_url: str) -> str:
    for domain, country in _DOMAIN_COUNTRY.items():
        if domain in source_url:
            return country
    return "United States"
