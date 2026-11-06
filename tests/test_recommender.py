import unittest

from recommender import CATEGORY_KEYWORDS, filter_articles


class FilterArticlesTest(unittest.TestCase):
    def setUp(self):
        self.articles = [
            {
                "title": "신규 XSS 취약점 발견",
                "link": "https://example.com/web",
                "date": "2026-11-01",
                "content": "웹 서비스 이용자는 보안 업데이트가 필요합니다.",
            },
            {
                "title": "기업 보안 동향",
                "link": "https://example.com/ransomware",
                "date": "2026-11-02",
                "content": "랜섬웨어 공격과 대응 방법을 소개합니다.",
            },
            {
                "title": "GDPR 준수 안내",
                "link": "https://example.com/privacy",
                "date": "2026-11-03",
                "content": "해외 진출 기업이 확인할 사항입니다.",
            },
            {
                "title": "OWASP가 분석한 MALWARE 공격",
                "link": "https://example.com/multiple",
                "date": "2026-11-04",
                "content": "여러 분야에 동시에 해당하는 기사입니다.",
            },
            {
                "title": "보안 교육 일정 안내",
                "link": "https://example.com/general",
                "date": "2026-11-05",
                "content": "다음 달 교육 신청을 받습니다.",
            },
            {
                "title": "정보 보호 기술 세미나",
                "link": "https://example.com/deidentification",
                "date": "2026-11-06",
                "content": "비식별 처리 기술의 최신 동향을 다룹니다.",
            },
        ]

    def test_category_names_are_fixed(self):
        self.assertEqual(
            set(CATEGORY_KEYWORDS), {"웹 보안", "악성코드", "개인정보"}
        )

    def test_each_category_can_be_selected_alone(self):
        self.assertEqual(
            filter_articles(self.articles, ["웹 보안"]),
            [self.articles[0], self.articles[3]],
        )
        self.assertEqual(
            filter_articles(self.articles, ["악성코드"]),
            [self.articles[1], self.articles[3]],
        )
        self.assertEqual(
            filter_articles(self.articles, ["개인정보"]),
            [self.articles[2], self.articles[5]],
        )

    def test_multiple_categories_do_not_duplicate_an_article(self):
        result = filter_articles(self.articles, ["웹 보안", "악성코드"])

        self.assertEqual(result, self.articles[:2] + [self.articles[3]])
        self.assertEqual(result.count(self.articles[3]), 1)

    def test_matches_title_and_content_case_insensitively(self):
        web_result = filter_articles(self.articles, ["웹 보안"])
        malware_result = filter_articles(self.articles, ["악성코드"])

        self.assertIn(self.articles[0], web_result)
        self.assertIn(self.articles[1], malware_result)
        self.assertIn(self.articles[3], malware_result)

    def test_no_selection_returns_all_articles_without_modifying_them(self):
        original_articles = [article.copy() for article in self.articles]

        result = filter_articles(self.articles, [])

        self.assertEqual(result, self.articles)
        self.assertIsNot(result, self.articles)
        self.assertEqual(self.articles, original_articles)

    def test_no_match_returns_empty_list(self):
        self.assertEqual(filter_articles([self.articles[4]], ["개인정보"]), [])


if __name__ == "__main__":
    unittest.main()
