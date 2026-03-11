"""MongoDB에 개발용 샘플 뉴스 데이터를 삽입하는 스크립트"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

PIN_COLORS = {
    "war": "#EF4444",
    "economy": "#16A34A",
    "politics": "#EAB308",
    "disaster": "#F97316",
}


def get_pin_size(importance: int) -> str:
    if importance >= 5:
        return "large"
    elif importance >= 3:
        return "medium"
    return "small"


SAMPLE_NEWS = [
    {
        "title": "[DUMMY] 중동 지역 군사 긴장 고조",
        "source": "Reuters (테스트)",
        "published_at": "2026-03-11T09:30:00Z",
        "summary": "[더미 데이터] 중동 지역에서 군사적 긴장이 다시 높아지고 있다. 주변국의 개입 가능성도 제기되고 있다.",
        "country": "Israel",
        "continent": "Asia",
        "region": "Middle East",
        "category": "war",
        "keywords": ["middle east", "military", "conflict"],
        "lat": 31.0461,
        "lng": 34.8516,
        "importance": 5,
        "ai_interpretation": "[더미] 이번 사건은 지역 안보 불안을 높이고 있다.",
        "ai_prediction": "[더미] 주변국 개입 가능성과 원자재 가격 변동성이 커질 수 있다.",
        "ai_impact": {"gold": "상승 가능성", "oil": "상승 가능성", "stocks": "하락 압력", "exchange_rate": "변동성 확대"},
    },
    {
        "title": "[DUMMY] 우크라이나 동부 전선 교착 상태 지속",
        "source": "BBC (테스트)",
        "published_at": "2026-03-10T14:00:00Z",
        "summary": "[더미 데이터] 우크라이나 동부 전선에서 양측의 교착 상태가 이어지고 있으며 외교적 해법이 모색되고 있다.",
        "country": "Ukraine",
        "continent": "Europe",
        "region": "Eastern Europe",
        "category": "war",
        "keywords": ["ukraine", "russia", "frontline"],
        "lat": 48.3794,
        "lng": 31.1656,
        "importance": 5,
        "ai_interpretation": "[더미] 장기화된 분쟁이 유럽 에너지 시장에 구조적 영향을 미치고 있다.",
        "ai_prediction": "[더미] 겨울철 에너지 수급 불안이 재차 부각될 가능성이 있다.",
        "ai_impact": {"gold": "보합", "oil": "상승 가능성", "stocks": "유럽 증시 불안", "exchange_rate": "유로화 약세 가능성"},
    },
    {
        "title": "[DUMMY] 미중 무역 관세 재협상 시작",
        "source": "Bloomberg (테스트)",
        "published_at": "2026-03-11T06:00:00Z",
        "summary": "[더미 데이터] 미국과 중국이 기존 관세 체계에 대한 재협상에 돌입했다. 글로벌 공급망에 미칠 영향이 주목된다.",
        "country": "United States",
        "continent": "NorthAmerica",
        "region": "North America",
        "category": "economy",
        "keywords": ["trade", "tariff", "us-china"],
        "lat": 38.9072,
        "lng": -77.0369,
        "importance": 5,
        "ai_interpretation": "[더미] 양국 관세 재협상은 글로벌 무역 질서 재편의 신호탄이 될 수 있다.",
        "ai_prediction": "[더미] 협상 결과에 따라 반도체·농산물 분야의 관세율이 조정될 전망이다.",
        "ai_impact": {"gold": "보합", "oil": "보합", "stocks": "기술주 변동성 확대", "exchange_rate": "달러 강세 가능성"},
    },
    {
        "title": "[DUMMY] 유럽중앙은행 기준금리 동결 결정",
        "source": "Financial Times (테스트)",
        "published_at": "2026-03-10T18:00:00Z",
        "summary": "[더미 데이터] ECB가 기준금리를 현 수준에서 동결했다. 인플레이션 둔화 추세 속에서도 신중한 입장을 유지했다.",
        "country": "Germany",
        "continent": "Europe",
        "region": "Western Europe",
        "category": "economy",
        "keywords": ["ecb", "interest rate", "inflation"],
        "lat": 50.1109,
        "lng": 8.6821,
        "importance": 4,
        "ai_interpretation": "[더미] ECB의 동결 결정은 인플레이션 대응과 경기 부양 사이 균형을 반영한다.",
        "ai_prediction": "[더미] 하반기 금리 인하 가능성이 시장에서 선반영될 수 있다.",
        "ai_impact": {"gold": "소폭 상승", "oil": "보합", "stocks": "유럽 증시 소폭 상승", "exchange_rate": "유로화 보합"},
    },
    {
        "title": "[DUMMY] 일본 엔화 약세 가속화",
        "source": "Nikkei (테스트)",
        "published_at": "2026-03-09T08:00:00Z",
        "summary": "[더미 데이터] 일본 엔화가 달러 대비 약세를 이어가고 있다. 일본은행의 통화정책 기조가 주요 원인으로 지목된다.",
        "country": "Japan",
        "continent": "Asia",
        "region": "East Asia",
        "category": "economy",
        "keywords": ["yen", "boj", "currency"],
        "lat": 35.6762,
        "lng": 139.6503,
        "importance": 3,
        "ai_interpretation": "[더미] 엔화 약세는 일본 수출기업에 유리하나 수입 물가 상승을 초래한다.",
        "ai_prediction": "[더미] 일본은행이 개입에 나설 가능성이 점차 높아지고 있다.",
        "ai_impact": {"gold": "보합", "oil": "보합", "stocks": "일본 수출주 강세", "exchange_rate": "엔화 추가 약세 가능성"},
    },
    {
        "title": "[DUMMY] 터키 남부 규모 6.2 지진 발생",
        "source": "AP (테스트)",
        "published_at": "2026-03-11T03:15:00Z",
        "summary": "[더미 데이터] 터키 남부에서 규모 6.2의 강진이 발생해 건물 붕괴와 인명 피해가 보고되고 있다.",
        "country": "Turkey",
        "continent": "Asia",
        "region": "Middle East",
        "category": "disaster",
        "keywords": ["earthquake", "turkey", "rescue"],
        "lat": 37.0,
        "lng": 35.3213,
        "importance": 5,
        "ai_interpretation": "[더미] 터키 남부는 지진 취약 지역으로, 반복적인 피해가 구조적 문제를 드러낸다.",
        "ai_prediction": "[더미] 국제 구호 활동이 확대되고 재건 관련 수요가 발생할 전망이다.",
        "ai_impact": {"gold": "보합", "oil": "보합", "stocks": "건설주 관심", "exchange_rate": "터키 리라 약세"},
    },
    {
        "title": "[DUMMY] 브라질 아마존 산불 확산 심각",
        "source": "CNN (테스트)",
        "published_at": "2026-03-08T20:00:00Z",
        "summary": "[더미 데이터] 브라질 아마존 열대우림에서 대규모 산불이 확산되고 있다. 건기 영향으로 진화가 어려운 상황이다.",
        "country": "Brazil",
        "continent": "SouthAmerica",
        "region": "South America",
        "category": "disaster",
        "keywords": ["amazon", "wildfire", "climate"],
        "lat": -3.4653,
        "lng": -62.2159,
        "importance": 4,
        "ai_interpretation": "[더미] 아마존 산불은 글로벌 탄소 흡수 능력 저하와 기후 변화 가속을 의미한다.",
        "ai_prediction": "[더미] 국제 사회의 환경 규제 강화 논의가 재점화될 수 있다.",
        "ai_impact": {"gold": "보합", "oil": "보합", "stocks": "탄소배출권 가격 상승", "exchange_rate": "헤알화 약세 가능성"},
    },
    {
        "title": "[DUMMY] 호주 동부 해안 사이클론 상륙 예고",
        "source": "ABC News (테스트)",
        "published_at": "2026-03-10T10:00:00Z",
        "summary": "[더미 데이터] 호주 동부 해안에 대형 사이클론이 접근 중이다. 퀸즐랜드 주 주민 대피가 시작되었다.",
        "country": "Australia",
        "continent": "Oceania",
        "region": "Oceania",
        "category": "disaster",
        "keywords": ["cyclone", "australia", "evacuation"],
        "lat": -27.4698,
        "lng": 153.0251,
        "importance": 3,
        "ai_interpretation": "[더미] 사이클론 상륙은 호주 농업과 물류에 단기적 충격을 줄 수 있다.",
        "ai_prediction": "[더미] 보험 청구 증가와 농산물 가격 변동이 예상된다.",
        "ai_impact": {"gold": "보합", "oil": "보합", "stocks": "호주 보험주 하락", "exchange_rate": "호주달러 소폭 약세"},
    },
    {
        "title": "[DUMMY] 미국 대선 후보 경선 본격 돌입",
        "source": "Washington Post (테스트)",
        "published_at": "2026-03-11T07:00:00Z",
        "summary": "[더미 데이터] 미국 대선 경선이 본격화되면서 주요 후보들의 정책 공약이 잇따라 발표되고 있다.",
        "country": "United States",
        "continent": "NorthAmerica",
        "region": "North America",
        "category": "politics",
        "keywords": ["election", "primary", "policy"],
        "lat": 38.9072,
        "lng": -77.0369,
        "importance": 4,
        "ai_interpretation": "[더미] 대선 경선은 향후 미국 외교·통상 정책의 방향을 결정짓는 중요한 변수이다.",
        "ai_prediction": "[더미] 후보별 정책 차이에 따라 특정 산업군의 주가가 선반영될 수 있다.",
        "ai_impact": {"gold": "보합", "oil": "보합", "stocks": "정책 수혜주 변동", "exchange_rate": "달러 변동성 확대"},
    },
    {
        "title": "[DUMMY] 아프리카연합 정상회의 개최",
        "source": "Al Jazeera (테스트)",
        "published_at": "2026-03-09T12:00:00Z",
        "summary": "[더미 데이터] 아프리카연합 정상회의가 개최되어 대륙 내 분쟁 해결과 경제 협력 방안이 논의되고 있다.",
        "country": "Ethiopia",
        "continent": "Africa",
        "region": "East Africa",
        "category": "politics",
        "keywords": ["african union", "summit", "diplomacy"],
        "lat": 9.0250,
        "lng": 38.7469,
        "importance": 3,
        "ai_interpretation": "[더미] AU 정상회의는 아프리카 내부 거버넌스 강화 시도를 보여준다.",
        "ai_prediction": "[더미] 대륙 내 무역 자유화와 인프라 투자 확대 논의가 진전될 수 있다.",
        "ai_impact": {"gold": "보합", "oil": "보합", "stocks": "아프리카 관련 ETF 관심", "exchange_rate": "보합"},
    },
    {
        "title": "[DUMMY] 한반도 비핵화 협상 재개 논의",
        "source": "Yonhap (테스트)",
        "published_at": "2026-03-10T09:00:00Z",
        "summary": "[더미 데이터] 한반도 비핵화를 위한 다자 협상 재개가 논의되고 있다. 관련국들의 입장 차이가 여전히 존재한다.",
        "country": "South Korea",
        "continent": "Asia",
        "region": "East Asia",
        "category": "politics",
        "keywords": ["denuclearization", "korea", "diplomacy"],
        "lat": 37.5665,
        "lng": 126.9780,
        "importance": 4,
        "ai_interpretation": "[더미] 비핵화 협상 재개는 동북아 안보 구도에 중대한 변화를 가져올 수 있다.",
        "ai_prediction": "[더미] 협상 진전 시 남북경협 관련 기대감이 시장에 반영될 수 있다.",
        "ai_impact": {"gold": "보합", "oil": "보합", "stocks": "남북경협주 관심", "exchange_rate": "원화 강세 가능성"},
    },
    {
        "title": "[DUMMY] 나이지리아 홍수 피해 확대",
        "source": "Reuters (테스트)",
        "published_at": "2026-03-07T15:00:00Z",
        "summary": "[더미 데이터] 나이지리아 남부 지역에서 폭우로 인한 홍수 피해가 확대되고 있다. 수만 명이 이재민이 되었다.",
        "country": "Nigeria",
        "continent": "Africa",
        "region": "West Africa",
        "category": "disaster",
        "keywords": ["flood", "nigeria", "humanitarian"],
        "lat": 6.5244,
        "lng": 3.3792,
        "importance": 2,
        "ai_interpretation": "[더미] 반복되는 홍수 피해는 기후 변화와 인프라 부족의 복합적 결과이다.",
        "ai_prediction": "[더미] 국제 인도주의 지원이 확대되고 인프라 투자 논의가 이어질 전망이다.",
        "ai_impact": {"gold": "보합", "oil": "나이지리아 원유 공급 차질 가능", "stocks": "보합", "exchange_rate": "나이라 약세"},
    },
]


async def seed():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB_NAME")]

    await db.news.delete_many({})
    await db.saved_articles.delete_many({})

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    for i, news in enumerate(SAMPLE_NEWS):
        news["pin_color"] = PIN_COLORS[news["category"]]
        news["pin_size"] = get_pin_size(news["importance"])
        news["url"] = f"https://example.com/dummy/{i}"
        news["created_at"] = now

    result = await db.news.insert_many(SAMPLE_NEWS)
    print(f"뉴스 {len(result.inserted_ids)}건 삽입 완료")

    await db.news.drop_indexes()
    await db.saved_articles.drop_indexes()

    await db.news.create_index([("category", 1)])
    await db.news.create_index([("continent", 1)])
    await db.news.create_index([("keywords", 1)])
    await db.news.create_index([("published_at", -1)])
    await db.news.create_index([("importance", -1)])
    await db.news.create_index([("title", "text"), ("summary", "text"), ("keywords", "text")])

    await db.saved_articles.create_index([("session_id", 1)])
    await db.saved_articles.create_index([("session_id", 1), ("article_id", 1)], unique=True)
    await db.saved_articles.create_index([("saved_at", -1)])
    await db.saved_articles.create_index([("category", 1)])
    await db.saved_articles.create_index([("continent", 1)])
    print("인덱스 생성 완료")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
