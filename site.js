// site.js — handles rendering for homepage and archive

(async function () {
  const cacheBuster = "?v=" + Date.now();

  async function loadManifest() {
    const res = await fetch("/posts/manifest.json" + cacheBuster, {
      headers: { "Accept": "application/json" },
    });
    if (!res.ok) throw new Error("Failed to fetch manifest.json");
    const data = await res.json();
    return Array.isArray(data.posts) ? data.posts : [];
  }

  function escapeHTML(str) {
    return (str || "").replace(/[&<>"']/g, function (m) {
      return ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      })[m];
    });
  }

  function formatDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    if (isNaN(d)) return "";
    return d.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "2-digit"
    });
  }

  function renderList(el, posts, limit) {
    if (!el) return;
    if (!posts.length) {
      el.innerHTML = `<li><em>No posts found.</em></li>`;
      return;
    }
    const slice = typeof limit === "number" ? posts.slice(0, limit) : posts;
    el.innerHTML = slice.map(p => {
      const title = escapeHTML(p.title || "Untitled");
      const href = "/" + (p.path || ("posts/" + (p.slug || "")));
      const date = formatDate(p.date_iso);
      return `<li><a href="${href}">${title}</a>${date ? ` <small>(${date})</small>` : ""}</li>`;
    }).join("");
  }

  try {
    const posts = await loadManifest();

    // Homepage list
    const latestList = document.getElementById("latest-posts");
    renderList(latestList, posts, 10);

    // Archive page list
    const allPostsList = document.getElementById("all-posts");
    renderList(allPostsList, posts);

  } catch (err) {
    console.error("Error loading posts:", err);
    const latestList = document.getElementById("latest-posts");
    const allPostsList = document.getElementById("all-posts");
    if (latestList) latestList.innerHTML = `<li><em>Error loading posts.</em></li>`;
    if (allPostsList) allPostsList.innerHTML = `<li><em>Error loading posts.</em></li>`;
  }
})();
