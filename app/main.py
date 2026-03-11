import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import connect_db, close_db
from app.routers import pages, news, articles


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(title="Global Issue Map", lifespan=lifespan)

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(pages.router)
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
