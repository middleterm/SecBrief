"""관심 분야 키워드로 보안 기사를 필터링한다."""

CATEGORY_KEYWORDS = {
    "웹 보안": [
        "웹 보안",
        "웹 해킹",
        "SQL Injection",
        "XSS",
        "CSRF",
        "OWASP",
        "취약점",
    ],
    "악성코드": [
        "악성코드",
        "랜섬웨어",
        "트로이목마",
        "스파이웨어",
        "봇넷",
        "malware",
    ],
    "개인정보": [
        "개인정보",
        "개인정보 유출",
        "비식별",
        "개인정보보호",
        "GDPR",
    ],
}


def filter_articles(
    articles: list[dict], selected_categories: list[str]
) -> list[dict]:
    """제목 또는 내용에 선택 분야의 키워드가 포함된 기사만 반환한다.

    선택 분야가 없으면 모든 기사를 반환한다. 알 수 없는 분야는 무시하며,
    한 기사가 여러 키워드나 분야에 일치해도 결과에는 한 번만 포함한다.
    """
    if not selected_categories:
        return list(articles)

    selected_keywords = {
        keyword.lower()
        for category in selected_categories
        for keyword in CATEGORY_KEYWORDS.get(category, [])
    }

    filtered_articles = []
    for article in articles:
        title = str(article.get("title") or "")
        content = str(article.get("content") or "")
        searchable_text = f"{title} {content}".lower()

        if any(keyword in searchable_text for keyword in selected_keywords):
            filtered_articles.append(article)

    return filtered_articles
