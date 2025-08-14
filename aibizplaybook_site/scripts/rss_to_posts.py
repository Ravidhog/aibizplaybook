import feedparser, os, datetime

FEEDS = [
    "https://feeds.feedburner.com/TechCrunch/artificial-intelligence",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"
]

POSTS_DIR = "posts"

def main():
    today = datetime.date.today().isoformat()
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            title = entry.title.replace("/", "-")
            filename = f"{today}-{title[:50].replace(' ', '_')}.md"
            path = os.path.join(POSTS_DIR, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"# {entry.title}\n\n{entry.link}\n\n{entry.summary[:200]}...")

if __name__ == "__main__":
    main()
