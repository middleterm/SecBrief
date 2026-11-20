import unittest
from types import SimpleNamespace
from unittest.mock import patch

from crawler import fetch_articles
from recommender import filter_articles


class IntegrationTest(unittest.TestCase):
    @patch(
        "crawler.feedparser.parse",
        return_value=SimpleNamespace(
            bozo=False,
            entries=[
                {
                    "title": "New Malware Attack",
                    "link": "https://example.com/1",
                    "summary": "A malware attack was reported.",
                },
                {
                    "title": "Security Training",
                    "link": "https://example.com/2",
                    "summary": "A general security article.",
                },
            ],
        ),
    )
    def test_crawler_and_recommender_work_together(self, mock_parse):
        articles = fetch_articles(
            "https://example.com/rss",
            limit=10,
            source="The Hacker News",
        )
        result = filter_articles(articles, [], ["MALWARE"])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["link"], "https://example.com/1")
        self.assertEqual(result[0]["source"], "The Hacker News")
        mock_parse.assert_called_once_with("https://example.com/rss")


if __name__ == "__main__":
    unittest.main()
