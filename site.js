// site.js — lightweight front-end for aibizplaybook
// - Renders latest posts to #latest-posts
// - Renders full archive to #all-posts (if present)
// - Injects /assets/ads.html into #ad-slot (if present)
// - Renders /assets/affiliates.json into #affiliates (if present)

(function () {
  // ---------- Small helpers ----------
  const bust = () => `?v=${Date.now()}`;

  function $(sel) {
    return document.querySelector(sel);
  }

  function escapeHTML(s) {
    return (s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function fmtDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    if (isNaN(d.getTime())) return "";
    return d.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "2-digit",
    });
  }

  async function fetchJSON(path) {
    const res = await fetch(path + bust(), { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error(`Failed to fetch ${path}`);
    return res.json();
  }

  async function fetchText(path) {
    const res = await fetch(path + bust());
    if (!res.ok) throw new Error(`Failed to fetch ${path}`);
    return res.text();
  }

  // ---------- Posts rendering ----------
  async function loadManifest() {
    try {
      const data = await fetchJSON("/posts/manifest.json");
      const posts = Array.isArray(data.posts) ? data.posts : [];
      // sort newest first if not already
      posts.sort((a, b) => String(b.date_iso).localeCompare(String(a.date_iso)));
      return posts;
    } catch (e) {
      console.error(e);
      return [];
    }
  }

  function postHref(p) {
    // Prefer explicit path from manifest; else build from slug
    return "/" + (p.path || ("posts/" + (p.slug || "")));
  }

  function postItemHTML(p) {
    const title = escapeHTML(p.title || "Untitled");
    const date = fmtDate(p.date_iso);
    const summary = escapeHTML(p.summary || "");
    return `
      <li class="post-item">
        <a class="post-link" href="${postHref(p)}">${title}</a>
        ${date ? ` <small class="post-date">(${date})</small>` : ""}
        ${summary ? `<div class="post-summary">${summary}</div>` : ""}
      </li>`;
  }

  async function renderLatest() {
    const mount = $("#latest-posts");
    if (!mount) return; // not on this page

    mount.innerHTML = `<li><em>Loading posts…</em></li>`;
    const posts = await loadManifest();

    if (!posts.length) {
      mount.innerHTML = `<li><em>No posts yet. Check back soon.</em></li>`;
      return;
    }

    const html = posts.slice(0, 10).map(postItemHTML).join("");
    mount.innerHTML = html;
  }

  async function renderAllPosts() {
    const mount = $("#all-posts");
    if (!mount) return; // not on this page

    mount.innerHTML = `<li><em>Loading posts…</em></li>`;
    const posts = await loadManifest();

    if (!posts.length) {
      mount.innerHTML = `<li><em>No posts yet.</em></li>`;
      return;
    }

    // Optional: simple alphabetical by date (already newest-first)
    const html = posts.map(postItemHTML).join("");
    mount.innerHTML = html;
  }

  // ---------- Ads + Affiliates (optional hooks) ----------
  async function renderAds() {
    const mount = $("#ad-slot");
    if (!mount) return;
    try {
      const html = await fetchText("/assets/ads.html");
      mount.innerHTML = html;
    } catch (e) {
      console.warn("ads.html missing or unreachable");
      mount.innerHTML = "";
    }
  }

  async function renderAffiliates() {
    const mount = $("#affiliates");
    if (!mount) return;

    try {
      const data = await fetchJSON("/assets/affiliates.json");
      const items = Array.isArray(data) ? data : (Array.isArray(data.items) ? data.items : []);
      if (!items.length) {
        mount.innerHTML = "";
        return;
      }
      // each item: { title, url, note } (flexible; extra fields ignored)
      mount.innerHTML = items
        .map((it) => {
          const t = escapeHTML(it.title || it.name || "Link");
          const u = escapeHTML(it.url || "#");
          const note = escapeHTML(it.note || "");
          return `<li><a href="${u}" rel="nofollow noopener noreferrer">${t}</a>${note ? ` — <small>${note}</small>` : ""}</li>`;
        })
        .join("");
    } catch (e) {
      console.warn("affiliates.json missing or invalid");
      mount.innerHTML = "";
    }
  }

  // ---------- Kickoff ----------
  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(() => {
    renderLatest();
    renderAllPosts();
    renderAds();
    renderAffiliates();
  });
})();
