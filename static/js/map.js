const TILE_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
const TILE_ATTR = '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>';

const PIN_RADIUS = { large: 14, medium: 10, small: 7 };

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

    marker.bindPopup(`
      <div class="popup-title">${pin.url ? `<a href="${pin.url}" target="_blank" rel="noopener">${pin.title}</a>` : pin.title}</div>
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
