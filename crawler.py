import feedparser
import requests

from bs4 import BeautifulSoup

from parser import (
    clean_content,
    extract_general_content,
    extract_kisa_content,
    get_rss_content,
)


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


def fetch_web_content(url, source=""):
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 SecBrief"},
            timeout=10,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        if source == "KISA 보호나라" or "boho.or.kr" in url:
            content = extract_kisa_content(soup)
        else:
            content = extract_general_content(soup)

        cleaned_lines = []
        for line in str(content).splitlines():
            line = clean_content(line)
            if line:
                cleaned_lines.append(line)
        return "\n".join(cleaned_lines)
    except Exception as error:
        print("원문 본문 수집 중 오류가 발생했습니다:", error)
        return ""


def refresh_article_contents(articles):
    updated_count = 0

    for article in articles:
        old_content = clean_content(article.get("content") or "")
        if old_content and old_content != "내용 없음":
            continue

        link = str(article.get("link") or "").strip()
        if not link:
            continue

        new_content = fetch_web_content(link, article.get("source", ""))
        if new_content:
            article["content"] = new_content
            updated_count += 1

    return updated_count


def fetch_articles(rss_url, limit=10, source="알 수 없는 출처"):
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

            if not title or not link:
                continue

            date = entry.get("published") or entry.get("updated") or "날짜 없음"
            content = get_rss_content(entry)

            if not content:
                content = fetch_web_content(link, source)
            if not content:
                content = "내용 없음"

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
