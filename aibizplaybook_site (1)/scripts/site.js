// Inject AdSense partial (assets/ads.html) if present
fetch('assets/ads.html').then(r => r.ok ? r.text() : '').then(html => {
  if (html) { const slot = document.getElementById('ad-slot'); if (slot) slot.innerHTML = html; }
}).catch(()=>{});

// Load affiliates list
fetch('assets/affiliates.json').then(r => r.ok ? r.json() : []).then(list => {
  const ul = document.getElementById('affiliates');
  if (!ul) return;
  if (Array.isArray(list) && list.length) {
    list.forEach(item => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = item.url;
      a.textContent = item.name || item.url;
      a.rel = "sponsored noopener";
      a.target = "_blank";
      li.appendChild(a);
      ul.appendChild(li);
    });
  } else {
    ul.innerHTML = '<li>Add links in assets/affiliates.json</li>';
  }
}).catch(()=>{});

// Build a simple list of posts by reading a manifest that rss_to_posts.py maintains
fetch('posts/manifest.json').then(r => r.ok ? r.json() : {posts:[]}).then(data => {
  const ul = document.getElementById('post-list');
  if (!ul) return;
  if (!data.posts || !data.posts.length) {
    ul.innerHTML = '<li>No posts yet. The Daily publisher will create them.</li>';
    return;
  }
  data.posts.slice(0, 20).forEach(p => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = 'posts/' + p.filename;
    a.textContent = p.title + ' — ' + p.date;
    li.appendChild(a);
    ul.appendChild(li);
  });
}).catch(()=>{});
