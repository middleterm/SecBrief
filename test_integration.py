from crawler import fetch_articles

articles = fetch_articles(
    "https://thehackernews.com/feeds/posts/default?alt=rss",
    limit=10
)

for article in articles:
    print(article["title"])