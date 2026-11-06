import os


API_KEY_PLACEHOLDER = "당신의_api 키"
MAX_CONTENT_LENGTH = 4000


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def summarize_article(article: dict) -> str:
    """기사 한 건을 한국어 3줄로 요약한다."""
    _load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key or api_key in {API_KEY_PLACEHOLDER, "당신의_api_키"}:
        return "API 키가 없어 요약을 생성할 수 없습니다.\n.env에 OPENAI_API_KEY를 설정하세요."

    title = str(article.get("title") or "제목 없음")
    content = str(article.get("content") or "내용 없음")[:MAX_CONTENT_LENGTH]

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=(
                "사이버보안 뉴스 편집자처럼 답하세요. "
                "기사 핵심을 한국어로 정확히 3줄로 요약하세요. "
                "각 줄은 한 문장으로 쓰고, 설명이나 제목은 덧붙이지 마세요."
            ),
            input=f"제목: {title}\n내용: {content}",
            max_output_tokens=250,
        )
        lines = [line.strip() for line in response.output_text.splitlines() if line.strip()]
        if len(lines) < 3:
            return "요약 형식이 올바르지 않습니다.\n잠시 후 다시 시도해주세요.\n원문 링크에서 전체 내용을 확인해주세요."
        return "\n".join(lines[:3])
    except Exception as exc:
        print("AI 요약 중 오류 발생:", exc)
        return "요약을 생성하지 못했습니다.\n원문 링크에서 기사 내용을 확인해주세요."
