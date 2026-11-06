from unittest.mock import patch
from types import SimpleNamespace
from crawler import fetch_articles

# 테스트용 가짜 RSS 데이터
fake_feed = SimpleNamespace(
    bozo=False,
    entries=[
        {
            "title": "정상 보안 기사",
            "link": "https://example.com/1",
            "summary": "정상적인 기사 내용"
        },
        {
            "title": "",
            "link": "https://example.com/2"
        },
        {
            "title": "링크 없는 기사",
            "link": ""
        }
    ]
)

# 실제 인터넷 대신 테스트용 데이터 사용
with patch("crawler.feedparser.parse", return_value=fake_feed):

    articles = fetch_articles(
        "https://example.com/rss",
        limit=10
    )

    # 정상 기사 1개만 남아야 함
    assert len(articles) == 1

    # 정상 기사 제목 확인
    assert articles[0]["title"] == "정상 보안 기사"

    # 딕셔너리 4개 키 확인
    assert set(articles[0].keys()) == {
        "title", "link", "date", "content"
    }

print("\n제목 및 링크 누락 테스트 성공!")
