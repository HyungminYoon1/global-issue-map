(function () {
  const map = createMap('map');
  let markers = [];
  let currentContinent = '';
  let selectedArticleId = null;

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
        closeDetail();
        loadArticles();
      });
      container.appendChild(btn);
    });
  }

  async function loadArticles() {
    let url = `/api/news/category/${PAGE_CATEGORY}?sort=importance`;
    if (currentContinent) url += `&continent=${currentContinent}`;

    try {
      const data = await apiFetch(url);
      clearMarkers(markers);
      markers = addPins(map, data.articles, onPinClick);
      renderList(data.articles);
      document.getElementById('articleCount').textContent = `${data.articles.length}건`;
    } catch (e) {
      showToast('데이터 로딩 실패', 'error');
    }
  }

  function renderList(articles) {
    const list = document.getElementById('articleList');
    if (!articles.length) {
      list.innerHTML = '<div class="empty-state">뉴스가 없습니다.</div>';
      return;
    }
    list.innerHTML = articles.map(a => `
      <div class="article-item" data-id="${a.id}">
        <div class="item-header">
          <span class="badge badge-${a.category}">${CATEGORY_LABELS[a.category] || a.category}</span>
        </div>
        <h4>${a.title}</h4>
        <div class="item-meta">
          <span>${a.source}</span>
          <span>${a.continent}</span>
          <span>중요도 ${a.importance}</span>
        </div>
      </div>
    `).join('');

    list.querySelectorAll('.article-item').forEach(item => {
      item.addEventListener('click', () => {
        openDetail(item.dataset.id);
      });
    });
  }

  function onPinClick(pin) {
    openDetail(pin.id);
    highlightListItem(pin.id);
  }

  function highlightListItem(id) {
    document.querySelectorAll('.article-item').forEach(el => {
      el.classList.toggle('selected', el.dataset.id === id);
    });
    const selected = document.querySelector(`.article-item[data-id="${id}"]`);
    if (selected) selected.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  async function openDetail(articleId) {
    selectedArticleId = articleId;
    highlightListItem(articleId);

    const panel = document.getElementById('detailPanel');
    const body = document.getElementById('detailBody');
    const saveBtn = document.getElementById('saveBtn');

    body.innerHTML = '<div class="empty-state">로딩 중...</div>';
    saveBtn.disabled = false;
    saveBtn.textContent = '기사 저장';
    saveBtn.classList.remove('saved');
    panel.classList.add('open');

    try {
      const detail = await apiFetch(`/api/news/${articleId}`);
      document.getElementById('detailTitle').textContent = detail.title;

      let html = `
        <div class="detail-meta">
          <span class="detail-meta-item">${detail.source}</span>
          <span class="detail-meta-item">${detail.continent} · ${detail.region}</span>
          <span class="detail-meta-item">${detail.country}</span>
          <span class="detail-meta-item">${detail.published_at?.slice(0, 10) || ''}</span>
        </div>
        <div class="detail-summary">${detail.summary}</div>
      `;

      if (detail.keywords?.length) {
        html += `<div class="detail-keywords">
          ${detail.keywords.map(k => `<span class="keyword-tag">${k}</span>`).join('')}
        </div>`;
      }

      html += '<div id="aiSection"><div class="empty-state" style="padding:20px">AI 분석 로딩 중...</div></div>';
      body.innerHTML = html;

      loadAiAnalysis(articleId);
    } catch (e) {
      body.innerHTML = '<div class="empty-state">상세 정보를 불러올 수 없습니다.</div>';
    }
  }

  async function loadAiAnalysis(articleId) {
    const section = document.getElementById('aiSection');
    try {
      const ai = await apiFetch(`/api/news/${articleId}/analysis`);
      if (!ai) {
        section.innerHTML = '';
        return;
      }

      const impactLabels = {
        gold: '금', oil: '유가', stocks: '주식', exchange_rate: '환율'
      };

      let html = '';
      if (ai.interpretation) {
        html += `
          <div class="ai-section">
            <h4>AI 해석</h4>
            <div class="ai-text">${ai.interpretation}</div>
          </div>`;
      }
      if (ai.prediction) {
        html += `
          <div class="ai-section">
            <h4>예상 동향</h4>
            <div class="ai-text">${ai.prediction}</div>
          </div>`;
      }
      if (ai.impact) {
        html += `
          <div class="ai-section">
            <h4>미치는 영향</h4>
            <div class="impact-grid">
              ${Object.entries(ai.impact).map(([k, v]) => `
                <div class="impact-item">
                  <div class="impact-label">${impactLabels[k] || k}</div>
                  <div class="impact-value">${v}</div>
                </div>
              `).join('')}
            </div>
          </div>`;
      }
      section.innerHTML = html;
    } catch {
      section.innerHTML = '';
    }
  }

  function closeDetail() {
    selectedArticleId = null;
    document.getElementById('detailPanel').classList.remove('open');
    document.querySelectorAll('.article-item').forEach(el => el.classList.remove('selected'));
  }

  document.getElementById('detailClose').addEventListener('click', closeDetail);

  document.getElementById('saveBtn').addEventListener('click', async () => {
    if (!selectedArticleId) return;
    const btn = document.getElementById('saveBtn');
    btn.disabled = true;
    try {
      await apiPost('/api/articles/save', { article_id: selectedArticleId });
      btn.textContent = '저장 완료';
      btn.classList.add('saved');
      showToast('기사가 저장되었습니다.', 'success');
    } catch {
      btn.disabled = false;
      showToast('저장에 실패했습니다.', 'error');
    }
  });

  buildContinentFilter();
  loadArticles();
})();
