from datetime import datetime, timedelta, timezone
from typing import Optional

from bson import ObjectId
from app.database import get_db

EXCLUDE_OTHERS = {"category": {"$ne": "others"}}


def _recent_filter() -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
    return {"created_at": {"$gte": cutoff}}


class NewsService:

    async def get_home_news(self, continent: Optional[str], keyword: Optional[str], limit: int) -> dict:
        db = get_db()
        query = {**EXCLUDE_OTHERS, **_recent_filter()}
        if continent:
            query["continent"] = continent
        if keyword:
            query["$text"] = {"$search": keyword}

        pin_cursor = db.news.find(query, {
            "_id": 0,
            "id": {"$toString": "$_id"},
            "title": 1,
            "continent": 1,
            "category": 1,
            "url": 1,
            "lat": 1,
            "lng": 1,
            "importance": 1,
            "pin_size": 1,
            "pin_color": 1,
        })
        map_pins = await pin_cursor.to_list(length=200)

        headline_fields = {
            "_id": 0,
            "id": {"$toString": "$_id"},
            "title": 1,
            "category": 1,
            "continent": 1,
            "region": 1,
            "source": 1,
            "summary": 1,
            "url": 1,
        }
        per_category = max(limit // 4, 2)
        top_headlines = []
        for cat in ("war", "economy", "disaster", "politics"):
            cat_query = {**query, "category": cat}
            cursor = db.news.find(cat_query, headline_fields).sort("importance", -1).limit(per_category)
            articles = await cursor.to_list(length=per_category)
            top_headlines.extend(articles)

        return {"map_pins": map_pins, "top_headlines": top_headlines}

    async def get_category_news(
        self, category: str, continent: Optional[str],
        keyword: Optional[str], sort: Optional[str], limit: Optional[int],
    ) -> dict:
        db = get_db()
        query = {"category": category, **_recent_filter()}
        if continent:
            query["continent"] = continent
        if keyword:
            query["$text"] = {"$search": keyword}

        sort_field = "importance" if sort == "importance" else "published_at"
        cursor = db.news.find(query, {
            "_id": 0,
            "id": {"$toString": "$_id"},
            "title": 1,
            "source": 1,
            "published_at": 1,
            "summary": 1,
            "country": 1,
            "continent": 1,
            "category": 1,
            "url": 1,
            "lat": 1,
            "lng": 1,
            "importance": 1,
            "pin_size": 1,
            "pin_color": 1,
        }).sort(sort_field, -1)

        if limit:
            cursor = cursor.limit(limit)

        articles = await cursor.to_list(length=limit or 50)
        return {"category": category, "articles": articles}

    async def get_continent_news(
        self, continent: str, category: Optional[str],
        keyword: Optional[str], limit: Optional[int],
    ) -> dict:
        db = get_db()
        query = {"continent": continent, **EXCLUDE_OTHERS, **_recent_filter()}
        if category:
            query["category"] = category
        if keyword:
            query["$text"] = {"$search": keyword}

        cursor = db.news.find(query, {
            "_id": 0,
            "id": {"$toString": "$_id"},
            "title": 1,
            "category": 1,
            "source": 1,
            "url": 1,
            "lat": 1,
            "lng": 1,
            "importance": 1,
            "pin_size": 1,
            "pin_color": 1,
        }).sort("importance", -1)

        if limit:
            cursor = cursor.limit(limit)

        articles = await cursor.to_list(length=limit or 50)
        return {"continent": continent, "articles": articles}

    async def search_news(
        self, query_text: str, continent: Optional[str],
        category: Optional[str], limit: int, page: int,
    ) -> dict:
        db = get_db()
        query = {"$text": {"$search": query_text}, **EXCLUDE_OTHERS, **_recent_filter()}
        if continent:
            query["continent"] = continent
        if category:
            query["category"] = category

        total = await db.news.count_documents(query)
        skip = (page - 1) * limit

        cursor = db.news.find(query, {
            "_id": 0,
            "id": {"$toString": "$_id"},
            "title": 1,
            "category": 1,
            "continent": 1,
            "source": 1,
            "summary": 1,
            "url": 1,
            "lat": 1,
            "lng": 1,
            "importance": 1,
            "pin_size": 1,
            "pin_color": 1,
        }).sort("importance", -1).skip(skip).limit(limit)

        articles = await cursor.to_list(length=limit)
        return {"query": query_text, "total": total, "page": page, "articles": articles}

    async def get_article_detail(self, article_id: str) -> dict:
        db = get_db()
        doc = await db.news.find_one(
            {"_id": ObjectId(article_id)},
            {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "title": 1,
                "source": 1,
                "published_at": 1,
                "summary": 1,
                "country": 1,
                "continent": 1,
                "region": 1,
                "category": 1,
                "keywords": 1,
                "url": 1,
                "lat": 1,
                "lng": 1,
                "importance": 1,
            },
        )
        return doc

    async def get_article_analysis(self, article_id: str) -> dict:
        db = get_db()
        doc = await db.news.find_one({"_id": ObjectId(article_id)})
        if not doc:
            return None

        cached = doc.get("ai_interpretation", "")
        is_dummy = not cached or cached.startswith("[더미]")

        if not is_dummy:
            return {
                "article_id": article_id,
                "interpretation": doc["ai_interpretation"],
                "prediction": doc["ai_prediction"],
                "impact": doc["ai_impact"],
            }

        from app.services.ai_service import AiService
        ai = AiService()
        result = await ai.analyze_article(doc)

        if result:
            await db.news.update_one(
                {"_id": ObjectId(article_id)},
                {"$set": {
                    "ai_interpretation": result["interpretation"],
                    "ai_prediction": result["prediction"],
                    "ai_impact": result["impact"],
                }},
            )
            return {"article_id": article_id, **result}

        return {
            "article_id": article_id,
            "interpretation": cached,
            "prediction": doc.get("ai_prediction", ""),
            "impact": doc.get("ai_impact", {}),
        }
