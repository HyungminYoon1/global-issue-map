import json
import logging

from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """당신은 세계 뉴스 분석 전문가입니다.
주어진 뉴스 기사 정보를 바탕으로 다음 3가지를 한국어로 분석해주세요.

반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트를 포함하지 마세요.

{
  "interpretation": "이 뉴스의 핵심 의미와 배경 분석 (2~3문장)",
  "prediction": "향후 예상되는 동향 (2~3문장)",
  "impact": {
    "gold": "금 시세 영향 (한 줄)",
    "oil": "유가 영향 (한 줄)",
    "stocks": "주식시장 영향 (한 줄)",
    "exchange_rate": "환율 영향 (한 줄)"
  }
}"""


def _build_user_prompt(article: dict) -> str:
    return f"""뉴스 제목: {article.get('title', '')}
카테고리: {article.get('category', '')}
국가/지역: {article.get('country', '')} ({article.get('region', '')})
대륙: {article.get('continent', '')}
요약: {article.get('summary', '')}
키워드: {', '.join(article.get('keywords', []))}"""


class AiService:

    async def analyze_article(self, article: dict) -> dict:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": _build_user_prompt(article)},
                ],
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            if not all(k in result for k in ("interpretation", "prediction", "impact")):
                raise ValueError("Missing required fields in AI response")

            return result
        except Exception as e:
            logger.error("AI 분석 실패: %s", e)
            return None
