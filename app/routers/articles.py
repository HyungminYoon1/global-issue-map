from fastapi import APIRouter, Depends, Request, Response
from typing import Optional

from app.models.article import SaveArticleRequest
from app.services.article_service import ArticleService
from app.session import get_session_id

router = APIRouter()
article_service = ArticleService()


@router.post("/save")
async def save_article(
    body: SaveArticleRequest,
    request: Request,
    response: Response,
    session_id: str = Depends(get_session_id),
):
    data = await article_service.save_article(body.article_id, session_id)
    return {"success": True, "message": "기사 저장 성공", "data": data}


@router.get("/saved")
async def get_saved_articles(
    request: Request,
    response: Response,
    category: Optional[str] = None,
    continent: Optional[str] = None,
    sort: Optional[str] = None,
    session_id: str = Depends(get_session_id),
):
    data = await article_service.get_saved_articles(session_id, category, continent, sort)
    return {"success": True, "message": "저장 기사 조회 성공", "data": data}


@router.delete("/saved/{saved_id}")
async def delete_saved_article(
    saved_id: str,
    request: Request,
    response: Response,
    session_id: str = Depends(get_session_id),
):
    data = await article_service.delete_saved_article(saved_id, session_id)
    return {"success": True, "message": "저장 기사 삭제 성공", "data": data}
