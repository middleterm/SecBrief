"""RSS에서 사이버 보안 기사를 가져오는 모듈."""

import html
import re

import feedparser


# 프로젝트에서 사용할 RSS 출처
RSS_SOURCES = {
    "1": {
        "name": "KISA 보호나라",
        "url": "https://www.boho.or.kr/kr/rss.do?bbsId=B0000133",
    },
    "2": {
        "name": "The Hacker News",
        "url": "https://thehackernews.com/feeds/posts/default?alt=rss",
    },
}


def clean_content(text):
    """HTML 태그와 불필요한 공백을 제거한다."""
    text = html.unescape(str(text))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_articles(rss_url, limit=10, source="알 수 없는 출처"):
    """RSS에서 최대 limit개의 기사를 수집해 공통 딕셔너리로 반환한다."""
    articles = []
    source = str(source or "알 수 없는 출처")

    if not rss_url or not rss_url.strip():
        print("오류: RSS 주소가 없습니다.")
        return articles

    if limit <= 0:
        print("오류: 기사 수는 1개 이상이어야 합니다.")
        return articles

    try:
        feed = feedparser.parse(rss_url)
        entries = getattr(feed, "entries", [])

        if getattr(feed, "bozo", False) and not entries:
            print("오류: RSS 데이터를 읽지 못했습니다.")
            print("원인:", getattr(feed, "bozo_exception", "알 수 없음"))
            return articles

        for entry in entries[:limit]:
            title = clean_content(entry.get("title") or "")
            link = str(entry.get("link") or "").strip()

            # 제목이나 원문 링크가 없는 항목은 저장하지 않는다.
            if not title or not link:
                continue

            date = entry.get("published") or entry.get("updated") or "날짜 없음"
            content = entry.get("summary") or entry.get("description") or "내용 없음"
            content = clean_content(content) or "내용 없음"

            article = {
                "title": title,
                "link": link,
                "date": str(date),
                "content": content,
                "source": source,
            }
            articles.append(article)

    except Exception as error:
        print("RSS 수집 중 오류가 발생했습니다:", error)
        return []

    print("수집한 기사 수:", len(articles))
    return articles
