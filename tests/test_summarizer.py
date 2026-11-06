import os
import sys
import types
import unittest
from unittest.mock import patch

from summarizer import summarize_article


class SummarizerTest(unittest.TestCase):
    def test_missing_api_key_does_not_call_ai(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "당신의_api 키"}, clear=True):
            self.assertIn("API 키가 없어", summarize_article({}))

    def test_returns_three_lines(self):
        class FakeResponse:
            output_text = "첫째 줄\n둘째 줄\n셋째 줄"

        class FakeClient:
            def __init__(self, api_key):
                self.responses = types.SimpleNamespace(
                    create=lambda **kwargs: FakeResponse()
                )

        fake_openai = types.SimpleNamespace(OpenAI=FakeClient)
        with patch.dict(
            os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True
        ), patch.dict(sys.modules, {"openai": fake_openai}):
            result = summarize_article(
                {"title": "테스트", "content": "보안 기사 내용"}
            )

        self.assertEqual(result.count("\n"), 2)


if __name__ == "__main__":
    unittest.main()
