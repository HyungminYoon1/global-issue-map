const TILE_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
const TILE_ATTR = '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>';

const PIN_RADIUS = { large: 10, medium: 7, small: 4 };

const CATEGORY_LABELS = {
  war: '전쟁', economy: '경제', disaster: '자연재해', politics: '정치'
};

const CONTINENTS = [
  { value: '', label: '전체' },
  { value: 'Asia', label: '아시아' },
  { value: 'Europe', label: '유럽' },
  { value: 'Africa', label: '아프리카' },
  { value: 'NorthAmerica', label: '북미' },
  { value: 'SouthAmerica', label: '남미' },
  { value: 'Oceania', label: '오세아니아' },
];

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

function addPins(map, pins, onClick) {
  const markers = [];
  pins.forEach(pin => {
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

    marker.bindPopup(`
      <div class="popup-title">${pin.title}</div>
      <div class="popup-meta">${CATEGORY_LABELS[pin.category] || pin.category}</div>
    `);

    if (onClick) {
      marker.on('click', () => onClick(pin));
    }

    marker._pinData = pin;
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
