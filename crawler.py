"""RSS와 원문 페이지에서 사이버 보안 기사를 가져오는 모듈."""

import feedparser
import requests

import html
import re

from bs4 import BeautifulSoup


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


def get_rss_content(entry):
    """RSS의 summary, description, content 순서로 내용을 찾는다."""
    content_fields = ["summary", "description", "content"]

    for field in content_fields:
        value = entry.get(field)

        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    item = item.get("value", "")
                content = clean_content(item)
                if content and content != "내용 없음":
                    return content
        else:
            if isinstance(value, dict):
                value = value.get("value", "")
            content = clean_content(value or "")
            if content and content != "내용 없음":
                return content

    return ""


def remove_unnecessary_tags(soup):
    """본문과 관계없는 HTML 태그와 영역을 제거한다."""
    remove_names = [
        "script",
        "style",
        "noscript",
        "nav",
        "header",
        "footer",
        "aside",
        "form",
        "iframe",
    ]

    for tag in soup.find_all(remove_names):
        tag.decompose()

    remove_words = [
        "gnb",
        "lnb",
        "menu",
        "navigation",
        "banner",
        "advert",
        "ads",
        "inquiry",
        "contact",
        "quick",
    ]

    for tag in soup.find_all(True):
        if tag.attrs is None:
            continue
        class_value = tag.get("class", [])
        if isinstance(class_value, list):
            class_value = " ".join(class_value)
        id_value = str(tag.get("id") or "")
        attributes = (str(class_value) + " " + id_value).lower()
        should_remove = False

        for word in remove_words:
            if word in attributes:
                should_remove = True
                break

        if should_remove:
            tag.decompose()


def is_noise_text(text):
    """본문에 포함하지 않을 메뉴·광고·문의 문구인지 확인한다."""
    noise_words = [
        "광고",
        "문의 사항",
        "문의사항",
        "문의처",
        "담당자",
        "전화번호",
        "이메일",
        "저작권",
        "copyright",
        "로그인",
        "회원가입",
        "검색",
        "참고사이트",
        "참고 사이트",
        "작성 :",
        "작성:",
    ]

    for noise_word in noise_words:
        if noise_word.lower() in text.lower():
            return True
    return False


def get_main_area(soup):
    """사이트에서 기사 본문 영역을 우선 선택한다."""
    content_area = soup.select_one(".content_html")
    if content_area is not None:
        return content_area

    article_area = soup.find("article")
    if article_area is not None:
        return article_area

    main_area = soup.find("main")
    if main_area is not None:
        return main_area

    return soup


def get_page_lines(soup):
    """페이지에서 메뉴·광고·문의 문구를 제외한 텍스트 줄을 만든다."""
    remove_unnecessary_tags(soup)
    lines = []
    page_text = get_main_area(soup).get_text("\n")
    for line in page_text.splitlines():
        line = clean_content(line)
        if len(line) < 2:
            continue

        if not is_noise_text(line) and line not in lines:
            lines.append(line)

    return lines


def is_section_line(line):
    """KISA 보안 공지의 주요 구역 제목인지 확인한다."""
    section_words = [
        "개요",
        "설명",
        "영향을 받는 제품",
        "영향받는 제품",
        "해결 방안",
        "해결방법",
        "해결 방법",
        "조치 방법",
    ]

    for section_word in section_words:
        normalized_line = line.strip(" :：-–")
        if normalized_line == section_word:
            return True
    return False


def extract_kisa_content(soup):
    """KISA 공지에서 개요·설명·영향 제품·해결 방안을 추출한다."""
    remove_unnecessary_tags(soup)
    content_area = soup.select_one(".content_html")

    # 현재 KISA 페이지는 content_html 안에 설명 문단과 제품 표가 있다.
    if content_area is not None:
        result = []
        for item in content_area.find_all(["p", "table"]):
            if item.name == "p":
                text = clean_content(item.get_text(" "))
                if text and not is_noise_text(text):
                    if "http://" not in text and "https://" not in text:
                        if not (
                            "영향을 받는 제품" in text
                            and "해결" in text
                        ):
                            result.append(text)
                continue

            table_rows = []
            for row in item.find_all("tr"):
                cells = []
                for cell in row.find_all(["th", "td"]):
                    cell_text = clean_content(cell.get_text(" "))
                    if cell_text:
                        cells.append(cell_text)
                if cells:
                    table_rows.append(" | ".join(cells))

            if table_rows:
                result.append("영향을 받는 제품 및 해결 방안:")
                for table_row in table_rows:
                    result.append(table_row)

        if result:
            return "\n".join(result)

    # 구조가 다른 KISA 페이지는 제목 줄을 기준으로 한 번 더 찾는다.
    lines = get_page_lines(soup)
    sections = [
        ("개요", ["개요"]),
        ("설명", ["설명"]),
        ("영향을 받는 제품", ["영향을 받는 제품", "영향받는 제품"]),
        ("해결 방안", ["해결 방안", "해결방법", "해결 방법", "조치 방법"]),
    ]
    result = []

    for section_name, section_labels in sections:
        start_index = -1
        for index, line in enumerate(lines):
            for label in section_labels:
                if label in line:
                    start_index = index
                    break
            if start_index >= 0:
                break

        if start_index < 0:
            continue

        section_lines = []
        first_line = lines[start_index]
        first_text = first_line
        for label in section_labels:
            first_text = first_text.replace(label, "", 1).strip(" :：-–")
        if first_text and first_text != first_line:
            section_lines.append(first_text)

        next_index = start_index + 1
        while next_index < len(lines):
            if is_section_line(lines[next_index]):
                break
            section_lines.append(lines[next_index])
            next_index += 1

        if section_lines:
            result.append(section_name + ": " + " ".join(section_lines))

    return "\n".join(result)


def extract_general_content(soup):
    """일반 보안 뉴스에서 본문 앞부분 3~5개 문장을 추출한다."""
    lines = get_page_lines(soup)
    paragraphs = []

    for paragraph in soup.find_all("p"):
        text = clean_content(paragraph.get_text(" "))
        if len(text) >= 20 and text not in paragraphs:
            paragraphs.append(text)

    if not paragraphs:
        for block in soup.find_all(["article", "main"]):
            text = clean_content(block.get_text(" "))
            if len(text) >= 20 and text not in paragraphs:
                paragraphs.append(text)

    if not paragraphs:
        paragraphs = lines

    all_text = " ".join(paragraphs)
    sentences = re.split(r"(?<=[.!?。！？])\s+", all_text)
    selected_sentences = []

    for sentence in sentences:
        sentence = clean_content(sentence)
        if len(sentence) < 20:
            continue
        selected_sentences.append(sentence)
        if len(selected_sentences) >= 5:
            break

    if selected_sentences:
        return " ".join(selected_sentences)

    return " ".join(paragraphs[:5])


def fetch_web_content(url, source=""):
    """원문 URL에서 기사 본문을 추출한다."""
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
    """저장된 기사 중 내용이 없는 기사의 본문을 다시 수집한다."""
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
    """RSS와 원문에서 최대 limit개의 기사를 수집한다."""
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
            content = get_rss_content(entry)

            # RSS에 내용이 없을 때만 원문 페이지를 추가로 확인한다.
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
