from pydantic import BaseModel


class SaveArticleRequest(BaseModel):
    article_id: str


class SavedArticle(BaseModel):
    id: str
    article_id: str
    title: str
    category: str
    continent: str
    region: str
    source: str
    summary: str
    saved_at: str
