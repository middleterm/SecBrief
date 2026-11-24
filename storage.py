"""기사와 사용자 키워드를 CSV/TXT 파일에 저장하고 읽는다."""

import csv
import os


BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_FOLDER, "data")
ARTICLES_FILE = os.path.join(DATA_FOLDER, "articles.csv")
KEYWORDS_FILE = os.path.join(DATA_FOLDER, "keywords.txt")
MEMOS_FILE = os.path.join(DATA_FOLDER, "memos.csv")
ARTICLE_FIELDS = ["title", "link", "date", "content", "source"]


def load_articles():
    articles = []

    try:
        with open(ARTICLES_FILE, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) < 4 or not row[0] or not row[1]:
                    continue

                article = {
                    "title": row[0],
                    "link": row[1],
                    "date": row[2] or "날짜 없음",
                    "content": row[3] or "내용 없음",   
                    "source": row[4] if len(row) >= 5 and row[4] else "기존 저장 기사",
                }
                articles.append(article)   
    except FileNotFoundError:
        return []
    except (OSError, csv.Error) as error:
        print("기사 파일을 읽는 중 오류가 발생했습니다:", error)
        return []

    return articles


def save_articles(articles):
    old_articles = load_articles()
    saved_links = []

    for article in old_articles:
        saved_links.append(article["link"])

    changed_count = 0
    for article in articles:
        title = str(article.get("title") or "").strip()
        link = str(article.get("link") or "").strip()

        if not title or not link:
            continue

        if link in saved_links:
            existing_index = saved_links.index(link)
            old_article = old_articles[existing_index]
            new_content = str(article.get("content") or "").strip()
            old_content = str(old_article.get("content") or "").strip()

            if (
                new_content
                and new_content != "내용 없음"
                and (not old_content or old_content == "내용 없음")
            ):
                old_article["content"] = new_content
                changed_count += 1
            continue

        old_articles.append(
            {
                "title": title,
                "link": link,
                "date": str(article.get("date") or "날짜 없음"),
                "content": str(article.get("content") or "내용 없음"),
                "source": str(article.get("source") or "알 수 없는 출처"),
            }
        )
        saved_links.append(link)
        changed_count += 1

    try:
        with open(ARTICLES_FILE, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(ARTICLE_FIELDS)
            for article in old_articles:
                writer.writerow(
                    [
                        article["title"],
                        article["link"],
                        article["date"],
                        article["content"],
                        article["source"],
                    ]
                )
    except OSError as error:
        print("기사 파일을 저장하는 중 오류가 발생했습니다:", error)
        return 0

    return changed_count


def load_keywords():
    keywords = []

    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as file:
            for line in file:
                keyword = line.strip()
                if keyword and not keyword.startswith("#"):
                    keywords.append(keyword)
    except FileNotFoundError:
        return []
    except OSError as error:
        print("키워드 파일을 읽는 중 오류가 발생했습니다:", error)
        return []

    return keywords


def save_keywords(keywords):
    clean_keywords = []

    for keyword in keywords:
        keyword = str(keyword).strip()
        duplicate = False
        for item in clean_keywords:
            if item.lower() == keyword.lower():
                duplicate = True
                break
        if keyword and not duplicate:
            clean_keywords.append(keyword)

    try:
        with open(KEYWORDS_FILE, "w", encoding="utf-8") as file:
            for keyword in clean_keywords:
                file.write(keyword + "\n")
    except OSError as error:
        print("키워드 파일을 저장하는 중 오류가 발생했습니다:", error)
        return None

    return clean_keywords


def load_memos():
    memos = {}

    try:
        with open(MEMOS_FILE, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 2 and row[0]:
                    memos[row[0]] = row[1]
    except FileNotFoundError:
        return {}
    except (OSError, csv.Error) as error:
        print("메모 파일을 읽는 중 오류가 발생했습니다:", error)
        return {}

    return memos


def save_memos(memos):

    try:
        with open(MEMOS_FILE, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["link", "memo"])
            for link in memos:
                if link:
                    writer.writerow([link, str(memos[link])])
    except OSError as error:
        print("메모 파일을 저장하는 중 오류가 발생했습니다:", error)
        return False

    return True
