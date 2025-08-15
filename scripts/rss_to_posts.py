#!/usr/bin/env python3
"""
rss_to_posts.py
- Fetches one or more RSS/Atom feeds
- Writes HTML posts into /posts
- Updates /posts/manifest.json with metadata
"""

import os
import re
import json
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import feedparser  # installed in the workflow

# --------------------------
# Config
# --------------------------
# Option A: Set a comma-separated list of feeds in repo/Actions secrets or env:
#   RSS_FEEDS="https://example.com/feed.xml,https://another.com/rss"
ENV_FEEDS = os.getenv("RSS_FEEDS", "").strip()

# Option B: Fallback list here (edit to your feeds if you prefer hardcoding)
FALLBACK_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
]

# How many items per feed to process on each run (avoid massive churn)
ITEMS_PER_FEED = int(os.getenv("ITEMS_PER_FEED", "20"))

# Where to write content
REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "posts"
MANIFEST_PATH = POSTS_DIR / "manifest.json"
ADS_SNIPPET = (REPO_ROOT / "assets" / "ads.html")  # optional include

# Site paths for assets (assumes root-deployed Pages)
STYLES_HREF = "/styles.css"
SCRIPT_SRC = "/site.js"

# --------------------------
# Utilities
# --------------------------

def ensure_dirs():
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

def load_manifest():
    if not MANIFEST_PATH.exists():
        return {"posts": []}
    try:
        with MANIFEST_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "posts" not in data or not isinstance(data["posts"], list):
            return {"posts": []}
        return data
    except Exception:
        # Corrupt or unreadable – reset safely
        return {"posts": []}

def save_manifest(manifest):
    # Keep posts sorted by date desc
    manifest["posts"].sort(key=lambda x: x.get("date_iso", ""), reverse=True)
    with MANIFEST_PATH.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

_slug_invalid = re.compile(r"[^a-z0-9\-]+")
def slugify(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"\s+", "-", text)
    text = _slug_invalid.sub("-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "post"

def pick_datetime(entry):
    # Prefer published, then updated, then now
    for key in ("published_parsed", "updated_parsed"):
        dt = getattr(entry, key, None)
        if dt:
            try:
                return datetime.fromtimestamp(time.mktime(dt), tz=timezone.utc)
            except Exception:
                pass
    return datetime.now(tz=timezone.utc)

def post_identity(entry):
    # Stable identity for dedupe: prefer entry.id, then link, then title+date hash
    if getattr(entry, "id", None):
        return entry.id
    if getattr(entry, "link", None):
        return entry.link
    base = (getattr(entry, "title", "") + "|" + getattr(entry, "summary", ""))[:512]
    return hashlib.sha1(base.encode("utf-8")).hexdigest()

def render_html(title, date_iso, content_html, source_link=None):
    ads_html = ""
    if ADS_SNIPPET.exists():
        try:
            ads_html = ADS_SNIPPET.read_text(encoding="utf-8")
        except Exception:
            ads_html = ""
    # Very minimal template; relies on /styles.css and /site.js living at the root
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="{STYLES_HREF}">
</head>
<body>
  <header>
    <h1>{title}</h1>
    <p><small>Published: {date_iso}</small></p>
  </header>

  <main>
    {content_html}
    {'<p><a href="%s" rel="noopener noreferrer">Source</a></p>' % source_link if source_link else ''}
  </main>

  <aside>
    {ads_html}
  </aside>

  <script src="{SCRIPT_SRC}"></script>
</body>
</html>
"""

def write_post_file(date_dt, title, content_html, source_link):
    # Name like: 2025-08-15-title-slug.html
    date_str = date_dt.strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{date_str}-{slug}.html"
    out_path = POSTS_DIR / filename
    html = render_html(title, date_dt.isoformat(), content_html, source_link)
    out_path.write_text(html, encoding="utf-8")
    return filename, out_path

def summarize_text(html, max_len=280):
    # crude fallback summary; many feeds already provide summaries
    txt = re.sub(r"<[^>]+>", " ", html or "")
    txt = re.sub(r"\s+", " ", txt).strip()
    if len(txt) > max_len:
        txt = txt[: max_len - 1].rstrip() + "…"
    return txt

# --------------------------
# Main
# --------------------------

def main():
    ensure_dirs()
    manifest = load_manifest()

    # Build a set of known IDs for dedupe
    known_ids = set(p.get("id") for p in manifest.get("posts", []) if p.get("id"))

    # Resolve feeds
    feeds = [u.strip() for u in (ENV_FEEDS.split(",") if ENV_FEEDS else FALLBACK_FEEDS) if u.strip()]
    if not feeds:
        print("No RSS feeds provided. Set RSS_FEEDS env or add to FALLBACK_FEEDS.")
        return

    added_count = 0
    for feed_url in feeds:
        print(f"Fetching: {feed_url}")
        parsed = feedparser.parse(feed_url)

        if parsed.bozo:
            print(f"  Warning: feedparser flagged a parsing issue: {parsed.bozo_exception}")
        if not parsed.entries:
            print("  No entries found.")
            continue

        for entry in parsed.entries[:ITEMS_PER_FEED]:
            pid = post_identity(entry)
            if pid in known_ids:
                # Already have it; skip
                continue

            title = getattr(entry, "title", "Untitled").strip() or "Untitled"
            link = getattr(entry, "link", None)
            date_dt = pick_datetime(entry)

            # Prefer full content, else summary
            content_html = ""
            if getattr(entry, "content", None):
                # Some feeds provide a list of content parts
                try:
                    content_html = " ".join([c.value for c in entry.content if getattr(c, "value", None)])
                except Exception:
                    pass
            if not content_html:
                content_html = getattr(entry, "summary", "") or ""

            filename, path = write_post_file(date_dt, title, content_html, link)
            print(f"  Wrote: posts/{filename}")

            # Add to manifest
            manifest["posts"].append({
                "id": pid,
                "title": title,
                "slug": filename,          # filename is effectively the slug here
                "path": f"posts/{filename}",
                "date_iso": date_dt.isoformat(),
                "source": link or "",
                "summary": summarize_text(content_html),
            })
            known_ids.add(pid)
            added_count += 1

    save_manifest(manifest)
    print(f"Done. New posts added: {added_count}")
    print(f"Manifest at: posts/manifest.json ({len(manifest['posts'])} total)")

if __name__ == "__main__":
    main()
