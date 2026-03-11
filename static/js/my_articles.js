(function () {
  const grid = document.getElementById('savedGrid');
  const filterCategory = document.getElementById('filterCategory');
  const filterContinent = document.getElementById('filterContinent');
  const filterSort = document.getElementById('filterSort');

  async function loadSaved() {
    let url = '/api/articles/saved?';
    const params = [];
    if (filterCategory.value) params.push(`category=${filterCategory.value}`);
    if (filterContinent.value) params.push(`continent=${filterContinent.value}`);
    if (filterSort.value) params.push(`sort=${filterSort.value}`);
    url += params.join('&');

    try {
      const data = await apiFetch(url);
      renderCards(data.articles);
    } catch {
      showToast('저장 기사 로딩 실패', 'error');
    }
  }

  function renderCards(articles) {
    if (!articles.length) {
      grid.innerHTML = '<div class="empty-state">저장된 기사가 없습니다.<br>카테고리 페이지에서 기사를 저장해보세요.</div>';
      return;
    }

    grid.innerHTML = articles.map(a => `
      <div class="saved-card" data-id="${a.id}">
        <div class="card-top">
          <h3>${a.title}</h3>
          <button class="delete-btn" data-id="${a.id}" title="삭제">&times;</button>
        </div>
        <div class="card-info">
          <span class="badge badge-${a.category}">${CATEGORY_LABELS[a.category] || a.category}</span>
          <span class="detail-meta-item">${a.continent} · ${a.region || ''}</span>
          <span class="detail-meta-item">${a.source}</span>
        </div>
        <p>${a.summary || ''}</p>
        <div class="card-date">저장일: ${a.saved_at?.slice(0, 10) || ''}</div>
      </div>
    `).join('');

    grid.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const id = btn.dataset.id;
        if (!confirm('이 기사를 삭제하시겠습니까?')) return;
        try {
          await apiDelete(`/api/articles/saved/${id}`);
          showToast('기사가 삭제되었습니다.', 'success');
          loadSaved();
        } catch {
          showToast('삭제에 실패했습니다.', 'error');
        }
      });
    });
  }

  filterCategory.addEventListener('change', loadSaved);
  filterContinent.addEventListener('change', loadSaved);
  filterSort.addEventListener('change', loadSaved);

  loadSaved();
})();
