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
    return "/" + (p.path || ("posts
