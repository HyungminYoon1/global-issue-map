const TILE_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
const TILE_ATTR = '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>';

const PIN_RADIUS = { large: 14, medium: 10, small: 7 };

/* ── i18n ── */
const _lang = localStorage.getItem('lang') || 'ko';

const _I18N = {
  ko: {
    nav_home: '홈', nav_war: '전쟁', nav_economy: '경제',
    nav_disaster: '자연재해', nav_politics: '정치', nav_my_articles: '나만의 기사',
    cat_war: '전쟁', cat_economy: '경제', cat_disaster: '자연재해',
    cat_politics: '정치', cat_others: '기타',
    cont_all: '전체', cont_asia: '아시아', cont_europe: '유럽',
    cont_africa: '아프리카', cont_north_america: '북미',
    cont_south_america: '남미', cont_oceania: '오세아니아',
    search_placeholder: '키워드 검색...', search_btn: '검색',
    top_headlines: '주요 뉴스',
    no_news: '표시할 뉴스가 없습니다.',
    no_articles: '뉴스가 없습니다.',
    loading: '로딩 중...',
    load_failed: '데이터 로딩 실패',
    save_article: '기사 저장', saved: '저장 완료',
    save_failed: '저장에 실패했습니다.', article_saved: '기사가 저장되었습니다.',
    delete_confirm: '이 기사를 삭제하시겠습니까?',
    deleted: '기사가 삭제되었습니다.', delete_failed: '삭제에 실패했습니다.',
    importance: '중요도',
    ai_interpretation: 'AI 해석', ai_prediction: '예상 동향', ai_impact: '미치는 영향',
    ai_loading: 'AI 분석 로딩 중...', ai_failed: 'AI 분석을 불러올 수 없습니다.',
    detail_failed: '상세 정보를 불러올 수 없습니다.',
    all_categories: '전체 카테고리', all_continents: '전체 대륙',
    sort_latest: '최신순', sort_category: '카테고리순',
    no_saved: '저장된 기사가 없습니다.', saved_hint: '카테고리 페이지에서 기사를 저장해보세요.',
    saved_date: '저장일', delete_title: '삭제',
    saved_articles_failed: '저장 기사 로딩 실패',
    articles_suffix: '건',
    impact_gold: '금', impact_oil: '유가', impact_stocks: '주식', impact_exchange_rate: '환율',
  },
  en: {
    nav_home: 'Home', nav_war: 'War', nav_economy: 'Economy',
    nav_disaster: 'Disaster', nav_politics: 'Politics', nav_my_articles: 'My Articles',
    cat_war: 'War', cat_economy: 'Economy', cat_disaster: 'Disaster',
    cat_politics: 'Politics', cat_others: 'Others',
    cont_all: 'All', cont_asia: 'Asia', cont_europe: 'Europe',
    cont_africa: 'Africa', cont_north_america: 'N. America',
    cont_south_america: 'S. America', cont_oceania: 'Oceania',
    search_placeholder: 'Search keywords...', search_btn: 'Search',
    top_headlines: 'Top Headlines',
    no_news: 'No news to display.',
    no_articles: 'No articles found.',
    loading: 'Loading...',
    load_failed: 'Failed to load data',
    save_article: 'Save Article', saved: 'Saved',
    save_failed: 'Failed to save.', article_saved: 'Article saved.',
    delete_confirm: 'Delete this article?',
    deleted: 'Article deleted.', delete_failed: 'Failed to delete.',
    importance: 'Importance',
    ai_interpretation: 'AI Interpretation', ai_prediction: 'Prediction', ai_impact: 'Impact Analysis',
    ai_loading: 'Loading AI analysis...', ai_failed: 'Failed to load AI analysis.',
    detail_failed: 'Failed to load details.',
    all_categories: 'All Categories', all_continents: 'All Continents',
    sort_latest: 'Latest', sort_category: 'By Category',
    no_saved: 'No saved articles.', saved_hint: 'Save articles from category pages.',
    saved_date: 'Saved', delete_title: 'Delete',
    saved_articles_failed: 'Failed to load saved articles',
    articles_suffix: '',
    impact_gold: 'Gold', impact_oil: 'Oil', impact_stocks: 'Stocks', impact_exchange_rate: 'Exchange Rate',
  },
};

function t(key) { return _I18N[_lang]?.[key] || _I18N['ko'][key] || key; }
function articleTitle(a) { return _lang === 'en' ? (a.title_en || a.title || '') : (a.title || ''); }
function articleSummary(a) { return _lang === 'en' ? (a.summary_en || a.summary || '') : (a.summary || ''); }

const CATEGORY_LABELS = _lang === 'en'
  ? { war: 'War', economy: 'Economy', disaster: 'Disaster', politics: 'Politics', others: 'Others' }
  : { war: '전쟁', economy: '경제', disaster: '자연재해', politics: '정치', others: '기타' };

const CONTINENTS = _lang === 'en'
  ? [
    { value: '', label: 'All' },
    { value: 'Asia', label: 'Asia' },
    { value: 'Europe', label: 'Europe' },
    { value: 'Africa', label: 'Africa' },
    { value: 'NorthAmerica', label: 'N. America' },
    { value: 'SouthAmerica', label: 'S. America' },
    { value: 'Oceania', label: 'Oceania' },
  ]
  : [
    { value: '', label: '전체' },
    { value: 'Asia', label: '아시아' },
    { value: 'Europe', label: '유럽' },
    { value: 'Africa', label: '아프리카' },
    { value: 'NorthAmerica', label: '북미' },
    { value: 'SouthAmerica', label: '남미' },
    { value: 'Oceania', label: '오세아니아' },
  ];

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const val = t(key);
    if (val !== key) el.textContent = val;
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
  });
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === _lang);
    btn.addEventListener('click', () => {
      if (btn.dataset.lang === _lang) return;
      localStorage.setItem('lang', btn.dataset.lang);
      location.reload();
    });
  });
});

function createMap(elementId) {
  const map = L.map(elementId, {
    center: [20, 0],
    zoom: 2,
    minZoom: 2,
    maxZoom: 10,
    zoomControl: true,
    worldCopyJump: true,
  });
  L.tileLayer(TILE_URL, { attribution: TILE_ATTR, subdomains: 'abcd' }).addTo(map);
  return map;
}

function spreadOverlapping(pins) {
  const OFFSET = 1.5;
  const coordCount = {};
  pins.forEach(p => {
    const key = `${p.lat},${p.lng}`;
    coordCount[key] = (coordCount[key] || 0) + 1;
  });

  const coordIdx = {};
  return pins.map(p => {
    const key = `${p.lat},${p.lng}`;
    const total = coordCount[key];
    if (total <= 1) return p;

    const idx = coordIdx[key] = (coordIdx[key] || 0) + 1;
    const angle = (2 * Math.PI * (idx - 1)) / total;
    return { ...p, lat: p.lat + OFFSET * Math.cos(angle), lng: p.lng + OFFSET * Math.sin(angle) };
  });
}

function addPins(map, pins, onClick) {
  const spread = spreadOverlapping(pins);
  const markers = [];
  spread.forEach((pin, i) => {
    const original = pins[i];
    const radius = PIN_RADIUS[pin.pin_size] || PIN_RADIUS.medium;
    const opacity = pin.pin_size === 'large' ? 1.0 : pin.pin_size === 'medium' ? 0.8 : 0.6;
    const marker = L.circleMarker([pin.lat, pin.lng], {
      radius,
      fillColor: pin.pin_color,
      color: pin.pin_color,
      weight: 1,
      fillOpacity: opacity,
      opacity: opacity,
    }).addTo(map);

    const pinTitle = articleTitle(pin);
    marker.bindPopup(`
      <div class="popup-title">${pin.url ? `<a href="${pin.url}" target="_blank" rel="noopener">${pinTitle}</a>` : pinTitle}</div>
      <div class="popup-meta">${CATEGORY_LABELS[pin.category] || pin.category}</div>
    `);

    marker.on('mouseover', function () {
      this.setRadius(radius + 4);
      this.setStyle({ fillOpacity: 1, weight: 2 });
    });
    marker.on('mouseout', function () {
      this.setRadius(radius);
      this.setStyle({ fillOpacity: opacity, weight: 1 });
    });

    if (onClick) {
      marker.on('click', () => onClick(original));
    }

    marker._pinData = original;
    markers.push(marker);
  });
  return markers;
}

function clearMarkers(markers) {
  markers.forEach(m => m.remove());
  markers.length = 0;
}

function showToast(message, type = '') {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = message;
  document.body.appendChild(el);
  requestAnimationFrame(() => el.classList.add('show'));
  setTimeout(() => {
    el.classList.remove('show');
    setTimeout(() => el.remove(), 300);
  }, 2500);
}

async function apiFetch(url) {
  const res = await fetch(url);
  const json = await res.json();
  if (!json.success) throw new Error(json.message);
  return json.data;
}

async function apiPost(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const json = await res.json();
  if (!json.success) throw new Error(json.message);
  return json.data;
}

async function apiDelete(url) {
  const res = await fetch(url, { method: 'DELETE' });
  const json = await res.json();
  if (!json.success) throw new Error(json.message);
  return json.data;
}
