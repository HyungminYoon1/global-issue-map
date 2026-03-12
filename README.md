# Global Issue Map

세계 주요 이슈를 지도 위에 시각화하여 한눈에 파악할 수 있는 웹 서비스입니다.

전쟁, 경제, 자연재해, 정치 등 글로벌 뉴스를 자동으로 수집하고, AI가 번역·분류·분석하여 인터랙티브 지도와 함께 제공합니다. **한국어/영어** 2개 국어를 지원합니다.

---

## 주요 기능

### 지도 기반 뉴스 시각화
- 세계 지도 위에 뉴스를 핀으로 표시하여 어디에서 무슨 일이 일어나고 있는지 직관적으로 확인
- 카테고리별 색상 구분 (전쟁: 빨강, 경제: 초록, 자연재해: 주황, 정치: 노랑)
- 중요도에 따른 핀 크기 차등, 호버 시 강조 효과
- 동일 좌표 핀 겹침 방지를 위한 자동 분산 배치

### 카테고리별 뉴스 탐색
- 전쟁 / 경제 / 자연재해 / 정치 4개 카테고리 전용 페이지
- 대륙별 필터로 관심 지역 뉴스만 조회
- 기사 클릭 시 상세 정보 및 원문 링크 제공

### AI 뉴스 분석
- GPT(gpt-4o-mini)를 활용한 뉴스 해석 및 향후 동향 예측
- 금, 유가, 주식, 환율 등 경제 지표에 미치는 영향 분석
- 분석 결과 캐싱으로 반복 조회 시 즉시 응답

### 자동 뉴스 수집
- GDELT, NewsData.io, GNews 등 다중 소스에서 3시간 간격으로 자동 수집
- **키워드 + GDELT Theme(주제) 합집합 검색**으로 누락 최소화
- 기사 원문 URL에서 리드 문단(300자)을 추출하여 분류 정확도 향상
- GPT를 통한 한국어 번역 및 카테고리 재분류 (제목 + 본문 기반)
- URL 기반 중복 방지, 신규 기사만 번역하여 비용 최적화
- 최근 48시간 이내 수집된 기사만 웹에 표시하여 항상 최신 뉴스를 제공
- 30일 경과 기사 자동 만료 (TTL 인덱스)

### 한국어/영어 2개 국어 지원
- 헤더의 KR/EN 토글 버튼으로 전체 UI 언어를 즉시 전환
- 네비게이션, 검색, 필터, 버튼 등 모든 UI 라벨이 선택 언어로 표시
- 기사 제목·요약도 한국어(GPT 번역) / 영어(GDELT 원문)로 전환
- 영어 원문은 수집 시 이미 저장되어 있어 추가 GPT 비용 없음
- 언어 설정은 브라우저에 저장되어 재방문 시에도 유지

### 기사 저장
- 관심 기사를 저장하여 나만의 기사 페이지에서 다시 확인
- 카테고리별, 대륙별 필터로 저장 기사 관리

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 백엔드 | FastAPI (Python) |
| 프론트엔드 | HTML / CSS / JavaScript + Jinja2 |
| 데이터베이스 | MongoDB Atlas |
| 지도 | Leaflet + OpenStreetMap |
| AI 분석 | OpenAI GPT (gpt-4o-mini) |
| 뉴스 소스 | GDELT (1차) → NewsData.io → GNews (폴백) |
| 다국어 | 한국어 / 영어 (클라이언트 전환) |
| 배포 | Render (Web Service) |

---

## 프로젝트 구조

```
global-issue-map/
├── app/
│   ├── main.py              # FastAPI 앱 + 자동 수집 스케줄러
│   ├── config.py             # 환경변수 설정
│   ├── database.py           # MongoDB 연결
│   ├── geo.py                # 국가/좌표 매핑
│   ├── session.py            # 세션 관리
│   ├── models/               # 데이터 모델
│   ├── routers/              # API 라우터 (news, articles, pages)
│   └── services/             # 비즈니스 로직
│       ├── news_service.py   # 뉴스 조회/검색/필터
│       ├── news_sources.py   # 뉴스 소스 API (GDELT, NewsData 등)
│       ├── article_service.py # 기사 저장/삭제
│       └── ai_service.py     # AI 분석
├── scripts/
│   └── collect_news.py       # 뉴스 수집 스크립트
├── static/
│   ├── css/style.css
│   └── js/                   # 프론트엔드 JS (map, home, category 등)
├── templates/                # Jinja2 HTML 템플릿
├── tests/                    # 테스트 스크립트
├── docs/                     # 설계 문서
├── requirements.txt
└── .env.example
```

---

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env.example`을 복사하여 `.env` 파일을 생성하고 값을 채웁니다.

```bash
cp .env.example .env
```

```
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net
MONGODB_DB_NAME=global_issue_map
OPENAI_API_KEY=sk-proj-...
NEWSDATA_API_KEY=pub_...
GNEWS_API_KEY=...
```

- `MONGODB_URI`, `OPENAI_API_KEY`는 필수입니다.
- `NEWSDATA_API_KEY`, `GNEWS_API_KEY`는 GDELT 실패 시 폴백용으로 사용됩니다.

### 3. 서버 실행

```bash
uvicorn app.main:app --reload
```

서버가 시작되면 `http://localhost:8000`에서 접속할 수 있으며, 자동으로 뉴스 수집이 시작됩니다 (5초 후 첫 수집, 이후 3시간 간격).

### 4. 수동 뉴스 수집 (선택)

서버와 별도로 뉴스를 즉시 수집하고 싶을 때 사용합니다.

```bash
python scripts/collect_news.py
```

### 5. 로컬 전체 실행 (Render 서버 없이)

Render 서버가 내려간 경우, 로컬에서 전체 서비스를 실행할 수 있습니다.

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. .env 파일이 있는지 확인 (없으면 .env.example 복사 후 값 입력)
# cp .env.example .env

# 3. 초기 뉴스 수집 (DB가 비어 있을 경우)
python scripts/collect_news.py

# 4. 서버 시작 (이후 3시간마다 자동 수집)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

브라우저에서 `http://localhost:8000`으로 접속하면 서비스를 이용할 수 있습니다.

---

## 페이지 구성

| 경로 | 설명 |
|------|------|
| `/` | 홈 - 전체 이슈 지도 + 주요 헤드라인 |
| `/war` | 전쟁 - 군사 충돌, 무력 분쟁 뉴스 |
| `/economy` | 경제 - 무역, 금융, 시장 뉴스 |
| `/disaster` | 자연재해 - 기후, 환경, 재해 뉴스 |
| `/politics` | 정치 - 외교, 선거, 정책 뉴스 |
| `/my-articles` | 나만의 기사 - 저장한 기사 관리 |

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/news/home` | 홈 지도 핀 + 헤드라인 |
| GET | `/api/news/category/{category}` | 카테고리별 뉴스 |
| GET | `/api/news/continent/{continent}` | 대륙별 뉴스 |
| GET | `/api/news/search?q=` | 뉴스 검색 |
| GET | `/api/news/{id}` | 기사 상세 |
| GET | `/api/news/{id}/analysis` | AI 분석 |
| POST | `/api/articles/save` | 기사 저장 |
| GET | `/api/articles/saved` | 저장 기사 목록 |
| DELETE | `/api/articles/saved/{id}` | 저장 기사 삭제 |

---

## 문서

- [요구사항 정의서](docs/requirements.md)
- [시스템 아키텍처](docs/system-architecture.md)
- [API 스펙](docs/api-spec.md)
