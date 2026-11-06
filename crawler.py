#현태방

#터미널에 pip install feedparser <-- 이거 입력하기(라이브러리 설치. 최초 1회만)


import feedparser
import html
import re

# 사용할 RSS 주소
RSS_SOURCES = {
    "1": {
        "name": "KISA 보호나라",
        "url": "https://www.boho.or.kr/kr/rss.do?bbsId=B0000133"
    },
    "2": {
        "name": "The Hacker News",
        "url": "https://thehackernews.com/feeds/posts/default?alt=rss"
    }
}


def clean_content(text):
    """HTML 태그와 특수문자를 정리한다."""
    text = html.unescape(str(text))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_articles(rss_url: str, limit: int = 10) -> list[dict]:
    """RSS에서 최대 limit개의 기사를 수집한다."""

    articles = []

    try:
        if not rss_url.strip():
            print("오류: RSS 주소가 없습니다.")
            return []

        if limit <= 0:
            print("오류: 기사 수는 1 이상이어야 합니다.")
            return []

        feed = feedparser.parse(rss_url)

        if feed.bozo and not feed.entries:
            print("오류: RSS 데이터를 읽지 못했습니다.")
            print("원인:", feed.bozo_exception)
            return []

        for entry in feed.entries[:min(limit, 10)]:

            title = clean_content(entry.get("title") or "")
            link = (entry.get("link") or "").strip()

            date = (
                entry.get("published")
                or entry.get("updated")
                or "날짜 없음"
            )

            content = (
                entry.get("summary")
                or entry.get("description")
                or "내용 없음"
            )

            content = clean_content(content)

            if not content:
                content = "내용 없음"

            # 제목이나 링크가 없으면 건너뛰기
            if not title or not link:
                continue

            article = {
                "title": title,
                "link": link,
                "date": str(date),
                "content": content
            }

            articles.append(article)

    except Exception as e:
        print("RSS 수집 중 오류 발생:", e)
        return []

    # 반환 직전 확인
    print("수집된 기사 수:", len(articles))

    if articles:
        print("첫 번째 기사:", articles[0])

    return articles


if __name__ == "__main__":

    print("================================")
    print("   SecBrief 보안 뉴스 수집기")
    print("================================")

    print("\n[RSS 출처 선택]")
    print("1. KISA 보호나라")
    print("2. The Hacker News")
    print("3. 직접 RSS 주소 입력")

    choice = input("\n번호 선택 (Enter = 1): ").strip()

    if choice == "":
        choice = "1"

    if choice in RSS_SOURCES:
        rss_url = RSS_SOURCES[choice]["url"]
        print("선택한 RSS:", RSS_SOURCES[choice]["name"])

    elif choice == "3":
        rss_url = input("RSS 주소를 입력하세요: ").strip()

    else:
        print("잘못된 선택입니다. 기본 KISA RSS를 사용합니다.")
        rss_url = RSS_SOURCES["1"]["url"]

    print("\n보안 뉴스를 수집하고 있습니다...\n")

    articles = fetch_articles(rss_url, limit=10)

    if articles:
        print("\n========== 기사 목록 ==========")

        for i, article in enumerate(articles, start=1):
            print(f"\n[{i}] {article['title']}")
            print("날짜:", article["date"])
            print("링크:", article["link"])
            print("내용:", article["content"])

    else:
        print("\n수집된 기사가 없습니다.")
        print("RSS 주소 또는 인터넷 연결을 확인해주세요.")
