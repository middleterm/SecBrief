"""관심 분야와 사용자가 입력한 키워드로 기사를 분류하는 모듈."""


# 기본으로 제공하는 관심 분야별 키워드
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
    "클라우드": [
        "클라우드",
        "cloud",
        "AWS",
        "Azure",
        "GCP",
        "Kubernetes",
    ],
}


def get_keywords(selected_categories, user_keywords=None):
    """선택한 분야와 사용자가 저장한 키워드를 하나의 목록으로 만든다."""
    if user_keywords is None:
        user_keywords = []

    keywords = []

    for category in selected_categories:
        category_keywords = CATEGORY_KEYWORDS.get(category, [])
        for keyword in category_keywords:
            duplicate = False
            for item in keywords:
                if item.lower() == keyword.lower():
                    duplicate = True
                    break
            if keyword and not duplicate:
                keywords.append(keyword)

    for keyword in user_keywords:
        keyword = str(keyword).strip()
        duplicate = False
        for item in keywords:
            if item.lower() == keyword.lower():
                duplicate = True
                break
        if keyword and not duplicate:
            keywords.append(keyword)

    return keywords


def filter_articles(articles, selected_categories, user_keywords=None):
    """제목 또는 내용에 키워드가 포함된 기사만 반환한다."""
    if user_keywords is None:
        user_keywords = []

    if not selected_categories and not user_keywords:
        return list(articles)

    keywords = get_keywords(selected_categories, user_keywords)
    filtered_articles = []

    for article in articles:
        title = str(article.get("title") or "")
        content = str(article.get("content") or "")
        searchable_text = (title + " " + content).lower()
        matched = False

        for keyword in keywords:
            if keyword.lower() in searchable_text:
                matched = True
                break

        # 여러 키워드에 일치해도 기사는 한 번만 추가한다.
        if matched:
            filtered_articles.append(article)

    return filtered_articles


def count_articles_by_keyword(articles, keywords):
    """각 키워드가 포함된 기사의 수를 계산한다."""
    counts = {}

    for keyword in keywords:
        count = 0
        lower_keyword = keyword.lower()

        for article in articles:
            title = str(article.get("title") or "")
            content = str(article.get("content") or "")
            searchable_text = (title + " " + content).lower()

            if lower_keyword in searchable_text:
                count += 1

        counts[keyword] = count

    return counts
