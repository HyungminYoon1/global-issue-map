import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import connect_db, close_db
from app.routers import pages, news, articles

logger = logging.getLogger(__name__)

COLLECT_INTERVAL_HOURS = 3


async def _run_collector():
    """백그라운드에서 뉴스 수집 스크립트를 주기적으로 실행."""
    await asyncio.sleep(5)
    while True:
        try:
            logger.info("뉴스 자동 수집 시작")
            from scripts.collect_news import main as collect_main
            from app.database import get_db
            await collect_main(db=get_db())
            logger.info("뉴스 자동 수집 완료")
        except Exception as e:
            logger.error("뉴스 자동 수집 실패: %s", e)
        await asyncio.sleep(COLLECT_INTERVAL_HOURS * 3600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    collector_task = asyncio.create_task(_run_collector())
    yield
    collector_task.cancel()
    await close_db()


app = FastAPI(title="Global Issue Map", lifespan=lifespan)

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(pages.router)
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
