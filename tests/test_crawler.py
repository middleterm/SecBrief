from unittest.mock import patch
from types import SimpleNamespace
from crawler import fetch_articles, fetch_web_content, refresh_article_contents

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
        limit=10,
        source="KISA 보호나라",
    )

    # 정상 기사 1개만 남아야 함
    assert len(articles) == 1

    # 정상 기사 제목 확인
    assert articles[0]["title"] == "정상 보안 기사"

    # 딕셔너리 5개 키 확인
    assert set(articles[0].keys()) == {
        "title", "link", "date", "content", "source"
    }
    assert articles[0]["source"] == "KISA 보호나라"

print("\n제목 및 링크 누락 테스트 성공!")


empty_content_feed = SimpleNamespace(
    bozo=False,
    entries=[
        {
            "title": "본문이 없는 기사",
            "link": "https://example.com/empty",
            "summary": "내용 없음",
            "description": "",
        }
    ],
)

with patch("crawler.feedparser.parse", return_value=empty_content_feed), patch(
    "crawler.fetch_web_content", return_value="원문에서 가져온 본문"
) as mock_fetch:
    articles = fetch_articles("https://example.com/rss", source="The Hacker News")

    assert articles[0]["content"] == "원문에서 가져온 본문"
    mock_fetch.assert_called_once_with("https://example.com/empty", "The Hacker News")


fake_response = SimpleNamespace(
    text="""
    <html>
      <nav>메뉴 광고 문의</nav>
      <main>
        <h2>개요</h2><p>제품 보안 취약점 개요입니다.</p>
        <h2>설명</h2><p>취약점의 자세한 설명입니다.</p>
        <h2>영향을 받는 제품</h2><p>제품 A와 제품 B입니다.</p>
        <h2>해결 방안</h2><p>최신 보안 업데이트를 설치하세요.</p>
      </main>
    </html>
    """,
    raise_for_status=lambda: None,
)

with patch("crawler.requests.get", return_value=fake_response):
    content = fetch_web_content(
        "https://www.boho.or.kr/kr/bbs/view.do?id=1",
        "KISA 보호나라",
    )

    assert "개요:" in content
    assert "영향을 받는 제품:" in content
    assert "해결 방안:" in content
    assert "메뉴" not in content


refresh_articles = [
    {
        "title": "내용 없음",
        "link": "https://example.com/empty",
        "date": "오늘",
        "content": "내용 없음",
        "source": "KISA 보호나라",
    },
    {
        "title": "기존 본문",
        "link": "https://example.com/full",
        "date": "오늘",
        "content": "이미 저장된 본문",
        "source": "KISA 보호나라",
    },
]

with patch("crawler.fetch_web_content", return_value="새로 수집한 본문") as mock_fetch:
    updated_count = refresh_article_contents(refresh_articles)

    assert updated_count == 1
    assert refresh_articles[0]["content"] == "새로 수집한 본문"
    assert refresh_articles[1]["content"] == "이미 저장된 본문"
    mock_fetch.assert_called_once()
