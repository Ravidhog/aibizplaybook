import os, json, datetime, re
    from pathlib import Path
    import feedparser
    from markdownify import markdownify as md

    FEEDS = [
        "https://openai.com/blog/rss/",
        "https://github.blog/changelog/feed/"
    ]

    SITE_TITLE = "AI Biz Playbook"
    OUT_DIR = Path("posts")
    OUT_DIR.mkdir(exist_ok=True)
    MANIFEST = OUT_DIR / "manifest.json"

    def slugify(s):
        s = re.sub(r'[^a-zA-Z0-9]+','-', s).strip('-').lower()
        return s or "post"

    def to_html(page_title, items):
        body = [f"<h2>{{page_title}}</h2>"]
        for it in items:
            body.append(f'<div class="post"><h3><a href="{{it["link"]}}" target="_blank" rel="noopener">{{it["title"]}}</a></h3>')
            summary = it.get("summary") or ""
            body.append(f"<p>{{summary}}</p>")
            body.append(f'<p class="meta">{{it.get("source","")}}</p></div>')
        content = "\n".join(body)
        return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{page_title}} — AI Biz Playbook</title><link rel="stylesheet" href="../styles.css"></head>
<body>
<header><h1><a href="../index.html" style="text-decoration:none;color:inherit;">AI Biz Playbook</a></h1></header>
<main>{{content}}</main>
<footer><p>&copy; {{year}} AI Biz Playbook</p></footer>
</body></html>""".format(page_title=page_title, content=content, year=datetime.datetime.utcnow().year)

    def fetch_all():
        items = []
        for url in FEEDS:
            d = feedparser.parse(url)
            for e in d.entries[:10]:
                items.append({
                    "title": e.get("title","(no title)"),
                    "link": e.get("link","#"),
                    "summary": e.get("summary",""),
                    "published": e.get("published",""),
                    "source": d.feed.get("title", url)
                })
        # sort newest first when possible
        def dt(x):
            try:
                return datetime.datetime(*x.get("published_parsed")).isoformat()
            except Exception:
                return ""
        items.sort(key=lambda x: dt(x), reverse=True)
        return items[:25]

    def main():
        items = fetch_all()
        if not items:
            print("No items found")
            return
        today = datetime.datetime.utcnow().date().isoformat()
        page_title = f"Daily Roundup — {{today}}"
        html = to_html(page_title, items)
        fname = f"{{today}}-roundup.html"
        (OUT_DIR / fname).write_text(html, encoding="utf-8")

        manifest = {"posts": []}
        if MANIFEST.exists():
            try:
                manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
            except Exception:
                manifest = {"posts": []}
        if not any(p.get("filename")==fname for p in manifest["posts"]):
            manifest["posts"].insert(0, {"filename": fname, "title": page_title, "date": today})
        MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print("Wrote", fname)

    if __name__ == "__main__":
        main()
