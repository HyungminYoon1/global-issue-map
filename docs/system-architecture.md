# Global Issue Map

## 시스템 아키텍처 문서

---

## 1. 시스템 개요

Global Issue Map은 전쟁, 경제, 자연재해, 정치 등 세계 주요 이슈를 **지도 기반으로 시각화**하여 사용자가 세계 상황을 한눈에 파악할 수 있도록 하는 웹 서비스이다.

사용자는 홈 화면에서 전체 이슈를 탐색하고, 카테고리 페이지에서 주제별 뉴스를 확인할 수 있으며, 관심 있는 기사를 저장해 **나만의 기사 페이지**에서 다시 확인할 수 있다. 또한 각 뉴스에 대해 AI 해석, 예상 동향, 영향 분석 정보를 제공한다. 

---

## 2. 시스템 목표

본 시스템의 목표는 다음과 같다.

* 세계 이슈를 지도 위 핀으로 직관적으로 표현
* 카테고리별, 대륙별 뉴스 탐색 기능 제공
* 뉴스 중요도에 따른 시각적 차별화
* 홈 화면에서 뉴스 검색 기능 제공
* AI 기반 뉴스 요약 및 영향 분석 제공
* 사용자의 기사 저장 및 관리 기능 제공

---

## 3. 시스템 구성 방향

본 시스템은 **가장 단순한 Python + MongoDB 구조**를 기반으로 설계한다.

### 선택 기술 스택

* **백엔드:** FastAPI
* **데이터베이스:** MongoDB Atlas
* **DB 접근:** PyMongo Async API
* **프론트엔드:** HTML / CSS / JavaScript + Jinja2 템플릿
* **지도:** Leaflet + OpenStreetMap
* **배포:** Render (Web Service)
* **확장 옵션:** 필요 시 일부 화면에만 Next.js 적용 가능

이 구조는 빠른 구현, 단순한 유지보수, 비교적 낮은 개발 복잡도를 목표로 한다.

---

## 4. 전체 시스템 아키텍처

```text
사용자 브라우저
      │
      ▼
Frontend (HTML/CSS/JS + Jinja2)
      │
      ▼
FastAPI Server
      │
 ┌───────────────┬───────────────┐
 ▼               ▼               ▼
News API      AI Analysis     MongoDB Atlas
(외부 뉴스)      Logic         (뉴스/저장기사)
```

---

## 5. 주요 구성 요소

### 5.1 Frontend

프론트엔드는 **정적 HTML/CSS/JS와 Jinja2 템플릿**을 사용하여 구성한다.
FastAPI가 템플릿 렌더링과 API 제공을 함께 담당한다.

#### 주요 역할

* 홈 / 전쟁 / 경제 / 자연재해 / 정치 / 나만의 기사 페이지 렌더링
* Leaflet + OpenStreetMap 기반 지도 표시 (다크 테마 타일)
* 뉴스 카드 표시 (기사 원문 링크 포함)
* 검색 UI 제공
* 대륙별 필터 UI 제공
* 저장 버튼 및 삭제 버튼 처리
* 뉴스 상세 정보 출력
* **한국어/영어 언어 전환** (헤더 KR/EN 토글)

#### 다국어 지원 (i18n)

* 지원 언어: 한국어(기본), 영어
* 헤더 네비바에 KR/EN 토글 버튼 배치
* 언어 전환 시 `localStorage`에 설정 저장 후 페이지 새로고침
* `data-i18n` 속성으로 정적 UI 텍스트(네비게이션, 버튼, 필터 등) 자동 번역
* 기사 제목/요약은 `title` ↔ `title_en`, `summary` ↔ `summary_en` 필드 전환
* 영어 콘텐츠는 GDELT 원문을 활용하므로 추가 GPT 비용 없음

#### 카테고리 색상 체계

| 카테고리 | 색상 | 표시명 |
|----------|------|--------|
| war | #EF4444 (빨강) | 전쟁 |
| economy | #16A34A (초록) | 경제 |
| disaster | #F97316 (주황) | 자연재해 |
| politics | #EAB308 (노랑) | 정치 |
| others | #94a3b8 (회색) | 기타 |

#### 지도 핀 기능

* 중요도에 따른 핀 크기 차등 (large: 14px, medium: 10px, small: 7px)
* 동일 좌표 핀 겹침 방지 (원형 분산 배치)
* 호버 시 핀 크기 확대 및 불투명도 강조 효과
* 핀 클릭 시 팝업 및 상세 정보 표시

#### 특징

* 단순한 구조로 빠른 개발 가능
* 초기 프로젝트에 적합
* 서버 렌더링 방식으로 구현 부담이 낮음

---

### 5.2 Backend

백엔드는 **FastAPI**를 사용한다.
FastAPI는 API 처리와 Jinja2 템플릿 렌더링을 함께 담당한다.

#### 주요 역할

* 페이지 라우팅
* 뉴스 조회 API 제공
* 뉴스 검색 API 제공
* 대륙별 뉴스 조회 API 제공
* 저장 기사 API 제공
* AI 분석 결과 반환
* 외부 뉴스 데이터 가공
* 뉴스 중요도 계산 및 전달

#### 페이지 라우트

* `/` : 홈 페이지
* `/war` : 전쟁 페이지
* `/economy` : 경제 페이지
* `/disaster` : 자연재해 페이지
* `/politics` : 정치 페이지
* `/my-articles` : 나만의 기사 페이지

#### API 엔드포인트

* `GET /api/news/home` : 홈 지도 뉴스 조회
* `GET /api/news/category/{category}` : 카테고리별 뉴스 조회
* `GET /api/news/continent/{continent}` : 대륙별 뉴스 조회
* `GET /api/news/search` : 뉴스 검색
* `GET /api/news/{article_id}` : 기사 상세 조회
* `GET /api/news/{article_id}/analysis` : AI 분석 조회
* `POST /api/articles/save` : 기사 저장
* `GET /api/articles/saved` : 저장 기사 목록 조회
* `DELETE /api/articles/saved/{saved_id}` : 저장 기사 삭제

---

### 5.3 Database

데이터베이스는 **MongoDB Atlas**를 사용한다.
MongoDB는 뉴스, AI 분석 결과, 사용자가 저장한 기사 정보를 문서 형태로 저장하기에 적합하다.

#### 저장 데이터

* 뉴스 데이터
* 뉴스 카테고리 정보
* 지도 좌표 정보
* 뉴스 중요도
* AI 분석 결과
* 저장한 기사 정보

#### 장점

* JSON 형태 데이터와 구조가 유사해 개발이 편함
* 뉴스처럼 필드 구성이 유동적인 데이터 저장에 유리
* Atlas를 통해 배포와 연결이 단순함

---

### 5.4 DB Access Layer

MongoDB 접근은 **PyMongo Async API**를 사용한다.

#### 역할

* 뉴스 문서 조회
* 카테고리별, 대륙별 뉴스 필터링
* 기사 저장 / 삭제 처리
* 검색 결과 조회
* AI 분석 데이터 저장 / 조회

이 계층은 FastAPI 라우터와 DB 사이를 분리하여 코드 구조를 깔끔하게 유지한다.

---

### 5.5 External News Source

외부 뉴스 API를 활용하여 세계 이슈를 수집한다. 수집은 `scripts/collect_news.py` 스크립트를 통해 주기적으로 실행된다 (3시간 간격).

#### 뉴스 소스 체인

| 순위 | 소스 | 특징 |
|------|------|------|
| 1차 | GDELT | 무제한, API 키 불필요, 이벤트 감지 + 지리 좌표 |
| 2차 | NewsData.io | GDELT 실패 시 자동 폴백, API 키 필요 |
| 3차 | GNews | NewsData 실패 시 자동 폴백, API 키 필요 |

1차 소스(GDELT)에서 수집 실패 시 2차 → 3차 순서로 자동 폴백하여 안정적인 수집을 보장한다.

#### GDELT 검색 전략: 키워드 + 주제(Theme) 합집합

GDELT에서 뉴스를 검색할 때 **키워드 기반 검색**과 **GDELT GKG 주제(Theme) 기반 검색**을 OR(합집합)으로 결합하여 포괄적인 수집을 보장한다.

* **키워드 검색**: 기사 본문/제목에 특정 단어가 포함된 기사를 검색
* **Theme 검색**: GDELT의 자연어 처리 엔진(GKG)이 기사 내용을 분석하여 자동 태깅한 주제 코드를 기반으로 검색

이 두 방식을 합집합으로 사용함으로써 키워드에 의존하는 경우 놓칠 수 있는 기사까지 수집한다.

| 카테고리 | 확장 키워드 | GDELT Theme 코드 |
|----------|------------|------------------|
| war | war, conflict, military, attack, troops, missile, airstrike, ceasefire, insurgency, bombing, invasion, combat, artillery, battlefield, warfare, occupation | MILITARY, ARMED_CONFLICT, TERROR |
| economy | economy, trade, inflation, GDP, market, tariff, recession, unemployment, stock, currency, debt, bankruptcy, "interest rate", "supply chain" | ECON_INFLATION, ECON_TRADE, ECON_STOCKMARKET, ECON_UNEMPLOYMENT |
| disaster | earthquake, flood, hurricane, wildfire, tsunami, cyclone, drought, volcano, tornado, avalanche, landslide, pandemic, epidemic, famine, storm, heatwave | NATURAL_DISASTER, ENV_CLIMATECHANGE, FAMINE, HEALTH_PANDEMIC |
| politics | election, president, parliament, diplomacy, summit, sanctions, coup, impeachment, referendum, legislation, protest, "prime minister", treaty, geopolitics | ELECTION, POLITICAL_TURMOIL, PROTEST, LEGISLATION |

#### 수집 흐름

1. 카테고리별(war, economy, disaster, politics) 뉴스 수집 (키워드 + Theme 합집합 쿼리)
2. 제목 유사도 60% 이상 기사 중복 제거
3. 중요도 산정
4. **기사 URL에서 리드 문단(300자) 추출** — meta description 또는 `<p>` 태그에서 본문 발췌
5. GPT(gpt-4o-mini)를 통한 한국어 번역 + 카테고리 재분류 (제목 + 본문 발췌 기반, 배치 처리)
6. MongoDB upsert (URL 기준 중복 방지)
7. 30일 초과 기사 자동 만료 (TTL 인덱스)

#### 본문 발췌를 통한 분류 정확도 향상

GDELT API는 기사 제목만 제공하고 본문이나 요약을 반환하지 않는다. 제목만으로는 정확한 카테고리 분류가 어려운 경우가 있다 (예: "UN Security Council Passes Resolution Demanding Iran Stop Attacks" — 제목에 "attacks"가 포함되어 war로 분류되지만, 실제 내용은 UN 결의안으로 politics에 해당).

이를 해결하기 위해 수집 단계에서 기사 원문 URL에 HTTP 요청을 보내 리드 문단(최대 300자)을 추출한다. 추출 우선순위:

1. HTML `<meta name="description">` 또는 `<meta property="og:description">` 태그
2. `<p>` 태그 텍스트 (script, style, nav 등 제외)

추출된 텍스트는 GPT에 제목과 함께 전달되어 더 정확한 분류를 가능하게 한다.

#### 카테고리 재분류

수집 시 GPT가 기사 제목과 본문 발췌를 종합 분석하여 5개 카테고리 중 가장 적합한 것으로 재분류한다.

* **war**: 실제 군사 교전, 전투 행위, 무력 공격, 폭격, 포격 등 직접적 무력 충돌 (개인 범죄 제외)
* **economy**: 경제, 무역, 금융, 주식, 환율, 물가, 관세, 경기침체, 유가, 에너지 시장
* **disaster**: 자연재해, 기후, 환경 오염, 전염병, 대형 사고
* **politics**: 정치, 외교, 선거, 정상회담, 제재, 법안, 정부 정책, UN/국제기구 결의, 외교적 대응, 평화 협상
* **others**: 위 4개에 해당하지 않는 기사 (범죄, 사건사고, 연예, 스포츠, 라이프스타일 등)

※ 전쟁 관련 맥락이라도 기사 주제가 외교·정치적 대응이면 politics, 경제적 영향이면 economy로 분류한다.

#### 수집 항목

* 뉴스 제목 (한국어 번역 + 원문 보존)
* 언론사
* 발행일
* 뉴스 요약 (한국어 번역 + 원문 보존)
* 국가 또는 지역
* 대륙
* 카테고리 (GPT 재분류 결과)
* 키워드
* 좌표 정보
* 중요도 정보
* 기사 원문 URL

---

### 5.6 AI Analysis Layer

AI 분석 계층은 뉴스 내용을 바탕으로 다음 정보를 생성한다.

* AI 해석
* 예상 동향
* 미치는 영향

#### 영향 분석 예시

* 전쟁: 금, 석유, 주식
* 경제: 환율, 금리, 시장
* 자연재해: 공급망, 교통, 산업
* 정치: 외교, 무역, 시장 심리

이 분석 결과는 카테고리 페이지 상세 화면에 표시된다. 

---

## 6. 페이지별 시스템 동작

### 6.1 홈 페이지

홈은 전체 세계 이슈를 보여주는 메인 대시보드이다.

#### 포함 기능

* 세계 지도 핀 표시
* 핀 색상으로 카테고리 구분
* 대륙별 뉴스 필터
* 뉴스 검색 기능
* 주요 뉴스 5개 카드 표시

#### 동작 흐름

1. 사용자 홈 접속
2. FastAPI가 MongoDB 또는 외부 뉴스 데이터 조회
3. Jinja2 템플릿에 뉴스 데이터 주입
4. 지도와 카드 렌더링
5. 사용자가 대륙 필터 선택 시 해당 대륙 뉴스만 조회
6. 사용자가 검색 시 검색 API 호출

---

### 6.2 카테고리 페이지

전쟁, 경제, 자연재해, 정치 페이지는 해당 주제 뉴스만 보여준다.

#### 포함 기능

* 카테고리별 지도
* 중요도에 따라 크기/강조가 다른 핀
* 대륙별 뉴스 필터
* 뉴스 상세 정보
* AI 분석 정보
* 기사 저장 버튼

#### 동작 흐름

1. 사용자 카테고리 페이지 접속
2. FastAPI가 해당 카테고리 뉴스 조회
3. 중요도에 따라 핀 데이터 가공
4. 템플릿 렌더링
5. 사용자가 대륙 필터 선택 시 해당 대륙 뉴스만 조회
6. 사용자가 핀 클릭 시 뉴스 상세/AI 분석 표시
7. 저장 버튼 클릭 시 저장 API 호출

---

### 6.3 나만의 기사 페이지

사용자가 저장한 기사를 관리하는 개인화 페이지이다.

#### 포함 기능

* 저장 기사 목록
* 기사 상세 확인
* 기사 삭제
* 카테고리별, 대륙별 분류

#### 동작 흐름

1. 사용자 나만의 기사 페이지 접속
2. FastAPI가 저장 기사 목록 조회
3. Jinja2로 목록 렌더링
4. 사용자가 삭제 시 삭제 API 호출

---

## 7. 데이터 흐름

### 7.1 뉴스 조회 흐름

```text
외부 뉴스 데이터 → FastAPI → MongoDB 저장/조회 → Jinja2 템플릿 렌더링 → 사용자 화면
```

### 7.2 검색 흐름

```text
사용자 검색 입력 → FastAPI 검색 API → MongoDB/뉴스 데이터 조회 → 검색 결과 반환 → 지도/리스트 업데이트
```

### 7.3 기사 저장 흐름

```text
사용자 저장 클릭 → FastAPI 저장 API → MongoDB 저장 → 나만의 기사 페이지 반영
```

### 7.4 AI 분석 흐름

```text
뉴스 데이터 → AI 분석 로직 → 분석 결과 저장/반환 → 카테고리 상세 영역 표시
```

---

## 8. 데이터 모델 개요

### 8.1 News Collection

* `_id`
* `title` — 한국어 번역된 제목
* `title_en` — 원문 영어 제목
* `source` — 언론사
* `published_at` — 기사 발행일
* `created_at` — DB 수집 시각 (48시간 필터 및 TTL 인덱스에 사용)
* `summary` — 한국어 번역된 요약
* `summary_en` — 원문 영어 요약
* `country` — 국가
* `continent` — 대륙
* `region` — 지역
* `category` — 카테고리 (war / economy / disaster / politics / others)
* `keywords` — 키워드 배열
* `url` — 기사 원문 URL
* `lat`, `lng` — 지도 좌표
* `importance` — 중요도 (1~5)
* `pin_size` — 핀 크기 (small / medium / large)
* `pin_color` — 핀 색상 (카테고리별 고유 색상)
* `ai_interpretation` — AI 해석 (캐싱)
* `ai_prediction` — AI 예상 동향 (캐싱)
* `ai_impact` — AI 영향 분석 (캐싱)

AI 분석 필드는 News 문서에 내장하여 단순한 구조를 유지한다. 최초 요청 시 gpt-4o-mini로 분석하고, 결과를 캐싱하여 이후 요청에서는 저장된 값을 반환한다.

#### 인덱스 구성

* `url` — unique 인덱스 (중복 수집 방지)
* `created_at` — TTL 인덱스 (30일 후 자동 만료)
* `category` — 카테고리별 조회 성능
* `continent` — 대륙별 조회 성능
* `importance` — 중요도순 정렬
* `published_at` — 발행일순 정렬

#### 조회 필터링 정책

* **48시간 필터**: 모든 목록 조회 API에서 `created_at` 기준 최근 48시간 이내 기사만 반환
* **others 제외**: 홈, 대륙별, 검색 조회에서 `others` 카테고리 기사를 자동 제외
* **카테고리별 헤드라인**: 홈 주요 뉴스는 4개 카테고리(war, economy, disaster, politics)에서 균등 배분

### 8.2 SavedArticles Collection

* `_id`
* `article_id`
* `title`
* `category`
* `continent`
* `region`
* `source`
* `summary`
* `saved_at`

---

## 9. 설계 장점

이 구조의 장점은 명확하다.

### 9.1 단순함

FastAPI 하나로 페이지 렌더링과 API 처리를 함께 할 수 있어 구조가 단순하다.

### 9.2 빠른 개발

Jinja2 기반 렌더링으로 프론트엔드 복잡도를 낮출 수 있다.

### 9.3 유지보수 용이

Python 중심 구조라 코드 관리가 쉽고, 기능 추가도 비교적 단순하다.

### 9.4 확장 가능성

초기에는 Jinja2로 시작하고, 필요 시 일부 화면만 Next.js로 분리할 수 있다.

---

## 10. 배포 구성

본 서비스는 **Render + MongoDB Atlas** 조합으로 배포한다.

### 배포 구조

```text
Render (Web Service)
  └── FastAPI + Jinja2 + Static Files
        │
        ▼
MongoDB Atlas (Cloud DB)
```

### Render 설정

* **런타임:** Python
* **빌드 명령어:** `pip install -r requirements.txt`
* **시작 명령어:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
* **환경변수:** `MONGODB_URI`, `MONGODB_DB_NAME`

### 선택 이유

* FastAPI 프로세스를 상시 유지하여 Jinja2 렌더링과 비동기 DB 연결을 안정적으로 운영할 수 있다.
* `uvicorn` 명령어 하나로 배포되어 별도 설정 파일이나 서버리스 어댑터가 불필요하다.
* MongoDB Atlas와 함께 외부 서버(EC2 등) 없이 전체 서비스를 운영할 수 있다.

---

## 11. 확장 방향

향후 다음과 같은 확장이 가능하다.

* 사용자 로그인 기능 추가
* 저장 기사 즐겨찾기 태그 기능
* 뉴스 실시간 갱신
* 핀 클러스터링
* Next.js 기반 프론트 분리
* AI 분석 고도화

---

## 12. 결론

Global Issue Map은 **FastAPI + MongoDB Atlas + Jinja2** 기반의 단순하고 실용적인 구조로 설계된 세계 이슈 시각화 서비스이다.

이 아키텍처는 현재 프로젝트 규모에 적합하며, 뉴스 지도 시각화, 카테고리 탐색, 검색, 기사 저장, AI 분석 기능을 효과적으로 구현할 수 있다. 또한 이후 필요에 따라 프론트엔드와 AI 기능을 점진적으로 확장할 수 있는 유연성을 가진다.


