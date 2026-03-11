from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

CATEGORY_MAP = {
    "war": "전쟁",
    "economy": "경제",
    "disaster": "자연재해",
    "politics": "정치",
}


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "active": "home",
    })


@router.get("/war")
async def war(request: Request):
    return templates.TemplateResponse("category.html", {
        "request": request,
        "active": "war",
        "category": "war",
        "label": CATEGORY_MAP["war"],
    })


@router.get("/economy")
async def economy(request: Request):
    return templates.TemplateResponse("category.html", {
        "request": request,
        "active": "economy",
        "category": "economy",
        "label": CATEGORY_MAP["economy"],
    })


@router.get("/disaster")
async def disaster(request: Request):
    return templates.TemplateResponse("category.html", {
        "request": request,
        "active": "disaster",
        "category": "disaster",
        "label": CATEGORY_MAP["disaster"],
    })


@router.get("/politics")
async def politics(request: Request):
    return templates.TemplateResponse("category.html", {
        "request": request,
        "active": "politics",
        "category": "politics",
        "label": CATEGORY_MAP["politics"],
    })


@router.get("/my-articles")
async def my_articles(request: Request):
    return templates.TemplateResponse("my_articles.html", {
        "request": request,
        "active": "my-articles",
    })
