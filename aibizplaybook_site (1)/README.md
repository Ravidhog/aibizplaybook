# AI Biz Playbook

Static site auto-publisher for GitHub Pages.

## Quick start
1) Settings → Pages → Deploy from a branch → `main` / root.  
2) Settings → Actions → Workflow permissions → **Read and write**.  
3) Actions → **Daily publisher** → **Run workflow** once to prime posts.  
4) (Optional) Add a custom domain by committing a `CNAME` file and setting DNS.

## Customization
- Edit RSS feeds in `scripts/rss_to_posts.py` (FEEDS list).
- Posting time: change the cron in `.github/workflows/publish.yml`.
- AdSense: paste snippet into `assets/ads.html`.
- Affiliates: edit `assets/affiliates.json`.
