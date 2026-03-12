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
      showToast(t('saved_articles_failed'), 'error');
    }
  }

  function renderCards(articles) {
    if (!articles.length) {
      grid.innerHTML = `<div class="empty-state">${t('no_saved')}<br>${t('saved_hint')}</div>`;
      return;
    }

    grid.innerHTML = articles.map(a => {
      const title = articleTitle(a);
      const summary = articleSummary(a);
      return `
      <div class="saved-card" data-id="${a.id}">
        <div class="card-top">
          <h3>${title}</h3>
          <button class="delete-btn" data-id="${a.id}" title="${t('delete_title')}">&times;</button>
        </div>
        <div class="card-info">
          <span class="badge badge-${a.category}">${CATEGORY_LABELS[a.category] || a.category}</span>
          <span class="detail-meta-item">${a.continent} · ${a.region || ''}</span>
          <span class="detail-meta-item">${a.source}</span>
        </div>
        <p>${summary}</p>
        <div class="card-date">${t('saved_date')}: ${a.saved_at?.slice(0, 10) || ''}</div>
      </div>
    `;
    }).join('');

    grid.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const id = btn.dataset.id;
        if (!confirm(t('delete_confirm'))) return;
        try {
          await apiDelete(`/api/articles/saved/${id}`);
          showToast(t('deleted'), 'success');
          loadSaved();
        } catch {
          showToast(t('delete_failed'), 'error');
        }
      });
    });
  }

  filterCategory.addEventListener('change', loadSaved);
  filterContinent.addEventListener('change', loadSaved);
  filterSort.addEventListener('change', loadSaved);

  loadSaved();
})();
