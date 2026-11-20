import unittest
from unittest.mock import mock_open, patch

import storage


class StorageTest(unittest.TestCase):
    def test_articles_are_saved_without_duplicate_links(self):
        articles = [
            {
                "title": "첫 기사",
                "link": "https://example.com/1",
                "date": "2026-11-01",
                "content": "내용",
            },
            {
                "title": "중복 기사",
                "link": "https://example.com/1",
                "date": "2026-11-02",
                "content": "다른 내용",
            },
        ]
        fake_file = mock_open()

        with patch.object(storage, "load_articles", return_value=[]), patch.object(
            storage, "ensure_data_folder"
        ), patch("storage.open", fake_file):
            added_count = storage.save_articles(articles)

        self.assertEqual(added_count, 1)
        self.assertTrue(fake_file.called)

    def test_keywords_are_saved_without_case_duplicates(self):
        fake_file = mock_open()

        with patch.object(storage, "ensure_data_folder"), patch(
            "storage.open", fake_file
        ):
            saved = storage.save_keywords(["Ransomware", "ransomware", "  XSS  "])

        self.assertEqual(saved, ["Ransomware", "XSS"])
        fake_file().write.assert_any_call("Ransomware\n")
        fake_file().write.assert_any_call("XSS\n")

    def test_keywords_are_loaded_line_by_line(self):
        fake_file = mock_open(read_data="Ransomware\n\nXSS\n")

        with patch("storage.open", fake_file):
            keywords = storage.load_keywords()

        self.assertEqual(keywords, ["Ransomware", "XSS"])

    def test_articles_are_loaded_from_csv_columns(self):
        fake_file = mock_open(
            read_data="title,link,date,content,source\n기사,https://example.com/1,오늘,내용,KISA 보호나라\n"
        )

        with patch("storage.open", fake_file):
            articles = storage.load_articles()

        self.assertEqual(articles[0]["title"], "기사")
        self.assertEqual(articles[0]["link"], "https://example.com/1")
        self.assertEqual(articles[0]["source"], "KISA 보호나라")

    def test_old_four_column_csv_keeps_all_data(self):
        fake_file = mock_open(
            read_data="title,link,date,content\n기사,https://example.com/1,오늘,내용\n"
        )

        with patch("storage.open", fake_file):
            articles = storage.load_articles()

        self.assertEqual(articles[0]["content"], "내용")
        self.assertEqual(articles[0]["source"], "기존 저장 기사")

    def test_missing_files_return_empty_lists(self):
        with patch("storage.open", side_effect=FileNotFoundError):
            self.assertEqual(storage.load_articles(), [])
            self.assertEqual(storage.load_keywords(), [])

    def test_keyword_save_error_returns_none(self):
        with patch.object(storage, "ensure_data_folder"), patch(
            "storage.open", side_effect=OSError
        ):
            self.assertIsNone(storage.save_keywords(["XSS"]))


if __name__ == "__main__":
    unittest.main()
