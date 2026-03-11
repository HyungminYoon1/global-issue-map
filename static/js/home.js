(function () {
  const map = createMap('map');
  let markers = [];
  let currentContinent = '';

  function buildContinentFilter() {
    const container = document.getElementById('continentFilter');
    CONTINENTS.forEach(c => {
      const btn = document.createElement('button');
      btn.className = 'continent-btn' + (c.value === '' ? ' active' : '');
      btn.textContent = c.label;
      btn.dataset.value = c.value;
      btn.addEventListener('click', () => {
        container.querySelectorAll('.continent-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentContinent = c.value;
        loadData();
      });
      container.appendChild(btn);
    });
  }

  async function loadData() {
    const keyword = document.getElementById('searchInput').value.trim();
    let url = '/api/news/home?limit=5';
    if (currentContinent) url += `&continent=${currentContinent}`;
    if (keyword) url += `&keyword=${encodeURIComponent(keyword)}`;

    try {
      const data = await apiFetch(url);
      clearMarkers(markers);
      markers = addPins(map, data.map_pins);
      renderHeadlines(data.top_headlines);
    } catch (e) {
      showToast('데이터 로딩 실패', 'error');
    }
  }

  function renderHeadlines(headlines) {
    const grid = document.getElementById('headlineGrid');
    if (!headlines.length) {
      grid.innerHTML = '<div class="empty-state">표시할 뉴스가 없습니다.</div>';
      return;
    }
    grid.innerHTML = headlines.map(h => `
      <div class="headline-card">
        <div class="card-meta">
          <span class="badge badge-${h.category}">${CATEGORY_LABELS[h.category] || h.category}</span>
          <span class="card-source">${h.source} · ${h.continent}</span>
        </div>
        <h3>${h.url ? `<a href="${h.url}" target="_blank" rel="noopener">${h.title}</a>` : h.title}</h3>
        <p>${h.summary || ''}</p>
      </div>
    `).join('');
  }

  document.getElementById('searchBtn').addEventListener('click', loadData);
  document.getElementById('searchInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') loadData();
  });

  buildContinentFilter();
  loadData();
})();
