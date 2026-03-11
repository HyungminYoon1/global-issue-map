from typing import Optional
from datetime import datetime, timezone

from bson import ObjectId
from app.database import get_db


class ArticleService:

    async def save_article(self, article_id: str, session_id: str) -> dict:
        db = get_db()
        news = await db.news.find_one({"_id": ObjectId(article_id)})
        if not news:
            return None

        existing = await db.saved_articles.find_one({
            "article_id": article_id,
            "session_id": session_id,
        })
        if existing:
            return {"saved_id": str(existing["_id"]), "article_id": article_id, "already_saved": True}

        saved_doc = {
            "session_id": session_id,
            "article_id": article_id,
            "title": news["title"],
            "category": news["category"],
            "continent": news["continent"],
            "region": news["region"],
            "source": news["source"],
            "summary": news["summary"],
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }

        result = await db.saved_articles.insert_one(saved_doc)
        return {"saved_id": str(result.inserted_id), "article_id": article_id}

    async def get_saved_articles(
        self, session_id: str,
        category: Optional[str], continent: Optional[str], sort: Optional[str],
    ) -> dict:
        db = get_db()
        query = {"session_id": session_id}
        if category:
            query["category"] = category
        if continent:
            query["continent"] = continent

        sort_field = "category" if sort == "category" else "saved_at"
        sort_order = 1 if sort == "category" else -1

        cursor = db.saved_articles.find(query, {
            "_id": 0,
            "id": {"$toString": "$_id"},
            "article_id": 1,
            "title": 1,
            "category": 1,
            "continent": 1,
            "region": 1,
            "source": 1,
            "summary": 1,
            "saved_at": 1,
        }).sort(sort_field, sort_order)

        articles = await cursor.to_list(length=100)
        return {"articles": articles}

    async def delete_saved_article(self, saved_id: str, session_id: str) -> dict:
        db = get_db()
        await db.saved_articles.delete_one({
            "_id": ObjectId(saved_id),
            "session_id": session_id,
        })
        return {"deleted_id": saved_id}
