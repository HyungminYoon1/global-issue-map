from fastapi import APIRouter, Query
from typing import Optional

from app.models.common import ApiResponse
from app.services.news_service import NewsService

router = APIRouter()
news_service = NewsService()


@router.get("/home", response_model=ApiResponse)
async def get_home_news(
    continent: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 5,
):
    data = await news_service.get_home_news(continent, keyword, limit)
    return ApiResponse(success=True, message="홈 뉴스 조회 성공", data=data)


@router.get("/category/{category}", response_model=ApiResponse)
async def get_category_news(
    category: str,
    continent: Optional[str] = None,
    keyword: Optional[str] = None,
    sort: Optional[str] = None,
    limit: Optional[int] = None,
):
    data = await news_service.get_category_news(category, continent, keyword, sort, limit)
    return ApiResponse(success=True, message="카테고리 뉴스 조회 성공", data=data)


@router.get("/continent/{continent}", response_model=ApiResponse)
async def get_continent_news(
    continent: str,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: Optional[int] = None,
):
    data = await news_service.get_continent_news(continent, category, keyword, limit)
    return ApiResponse(success=True, message="대륙별 뉴스 조회 성공", data=data)


@router.get("/search", response_model=ApiResponse)
async def search_news(
    q: str = Query(...),
    continent: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 10,
    page: int = 1,
):
    data = await news_service.search_news(q, continent, category, limit, page)
    return ApiResponse(success=True, message="검색 성공", data=data)


@router.get("/{article_id}", response_model=ApiResponse)
async def get_article_detail(article_id: str):
    data = await news_service.get_article_detail(article_id)
    return ApiResponse(success=True, message="기사 상세 조회 성공", data=data)


@router.get("/{article_id}/analysis", response_model=ApiResponse)
async def get_article_analysis(article_id: str):
    data = await news_service.get_article_analysis(article_id)
    return ApiResponse(success=True, message="AI 분석 조회 성공", data=data)
