/* Leaflet and Turf are distributed locally with their license notices. */
const map = L.map('map').setView([55.6761, 12.5683], 16);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  maxZoom: 19
}).addTo(map);
const reportLayer = L.layerGroup().addTo(map);
const draftLayer = L.layerGroup().addTo(map);
const container = document.getElementById('map');
const useButton = document.getElementById('use');
const undoButton = document.getElementById('undo');
const clearButton = document.getElementById('clear');
const status = document.getElementById('status');
let mode = 'move';
let strokes = [];
let point = null;
let activeStroke = null;
let previewLine = null;
let selection = null;
let currentCity = '';
let lastReports = '';
let serverSelection = '';

function send(type, extra = {}) {
  window.parent.postMessage({isStreamlitMessage: true, type, ...extra}, '*');
}
function resize() { send('streamlit:setFrameHeight', {height: document.body.scrollHeight + 4}); }
new ResizeObserver(resize).observe(document.body);

function popup(report) {
  const element = document.createElement('div');
  for (const [index, text] of [report.type, report.description, report.restrictions,
    `Reported ${report.created} · ${report.upvotes} agree · ${report.downvotes} disagree`].entries()) {
    const line = document.createElement(index === 0 ? 'strong' : 'span');
    line.className = 'report-detail';
    line.textContent = text;
    element.appendChild(line);
  }
  return element;
}

function setMode(nextMode) {
  if (activeStroke) finishStroke(true);
  mode = nextMode;
  container.classList.toggle('highlight', mode === 'highlight');
  container.classList.toggle('spot', mode === 'spot');
  document.querySelectorAll('[data-mode]').forEach(button => {
    button.setAttribute('aria-pressed', String(button.dataset.mode === mode));
  });
  document.getElementById('brush-label').hidden = mode !== 'highlight';
  const drawing = mode === 'highlight';
  for (const handler of [map.dragging, map.touchZoom, map.doubleClickZoom, map.scrollWheelZoom]) {
    if (drawing) handler.disable(); else handler.enable();
  }
  document.getElementById('instruction').textContent = {
    move: 'Drag to explore. Choose Mark a spot or Highlight area to start a report.',
    spot: 'Tap the exact spot, then choose Use selected location.',
    highlight: 'Drag over the parking spaces. Lift your finger to finish each stroke. Choose Move map to pan or zoom.'
  }[mode];
  resize();
}

function updateDraft() {
  draftLayer.clearLayers();
  selection = null;
  try {
    if (strokes.length) {
      const buffered = strokes.map(stroke => turf.buffer(turf.lineString(stroke.points), stroke.width / 2, {units: 'meters', steps: 8}));
      const area = buffered.length === 1 ? buffered[0] : turf.union(turf.featureCollection(buffered));
      const center = turf.pointOnFeature(area).geometry.coordinates;
      selection = {geometry: area.geometry, lng: center[0], lat: center[1]};
      L.geoJSON(area, {style: {color: '#17674d', fillColor: '#48bb78', weight: 2, fillOpacity: .45}}).addTo(draftLayer);
    } else if (point) {
      selection = {geometry: null, ...point};
      L.circleMarker([point.lat, point.lng], {radius: 9, color: '#17674d', fillOpacity: .8}).addTo(draftLayer);
    }
  } catch (error) {
    status.textContent = 'This stroke could not be converted to an area. Undo it and try again.';
  }
  undoButton.disabled = !strokes.length;
  clearButton.disabled = !strokes.length && !point;
  useButton.disabled = !selection;
}

map.on('click', event => {
  if (mode !== 'spot') return;
  strokes = [];
  point = {lat: event.latlng.lat, lng: event.latlng.lng};
  status.textContent = 'Check the marked location, then confirm it.';
  updateDraft();
});

container.addEventListener('pointerdown', event => {
  if (mode !== 'highlight' || event.button !== 0 || !event.isPrimary || event.target.closest('.leaflet-control')) return;
  event.preventDefault();
  container.setPointerCapture(event.pointerId);
  const latlng = map.mouseEventToLatLng(event);
  activeStroke = {pointer: event.pointerId, points: [[latlng.lng, latlng.lat]], width: Number(document.getElementById('brush-width').value)};
  previewLine = L.polyline([latlng], {color: '#48bb78', weight: 12, opacity: .7, interactive: false}).addTo(map);
});
container.addEventListener('pointermove', event => {
  if (!activeStroke || activeStroke.pointer !== event.pointerId) return;
  event.preventDefault();
  const latlng = map.mouseEventToLatLng(event);
  const previous = activeStroke.points[activeStroke.points.length - 1];
  if (map.latLngToContainerPoint([previous[1], previous[0]]).distanceTo(map.latLngToContainerPoint(latlng)) < 3) return;
  activeStroke.points.push([latlng.lng, latlng.lat]);
  previewLine.addLatLng(latlng);
});
function finishStroke(cancelled = false) {
  if (!activeStroke) return;
  const completed = activeStroke;
  activeStroke = null;
  if (container.hasPointerCapture(completed.pointer)) container.releasePointerCapture(completed.pointer);
  map.removeLayer(previewLine);
  if (!cancelled && completed.points.length > 1) {
    point = null;
    strokes.push(completed);
    status.textContent = 'Area highlighted. Add another stroke, undo, or use this selection.';
  } else {
    status.textContent = 'Drag a short stroke over the parking spaces to highlight them.';
  }
  previewLine = null;
  updateDraft();
}
container.addEventListener('pointerup', () => finishStroke());
container.addEventListener('pointercancel', () => finishStroke(true));
container.addEventListener('lostpointercapture', () => { if (activeStroke) finishStroke(true); });
document.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => setMode(button.dataset.mode)));
undoButton.addEventListener('click', () => { strokes.pop(); updateDraft(); });
clearButton.addEventListener('click', () => { strokes = []; point = null; updateDraft(); status.textContent = 'Selection cleared.'; });
useButton.addEventListener('click', () => {
  if (!selection) return;
  send('streamlit:setComponentValue', {value: {...selection, id: crypto.randomUUID()}, dataType: 'json'});
  status.textContent = 'Location confirmed. Continue with the description below the map.';
  setMode('move');
});

window.addEventListener('message', event => {
  if (event.source !== window.parent || !event.data || event.data.type !== 'streamlit:render') return;
  const args = event.data.args;
  const city = JSON.stringify(args.center);
  if (city !== currentCity) {
    map.setView(args.center, 16);
    currentCity = city;
  }
  const reportData = JSON.stringify(args.reports);
  if (reportData !== lastReports) {
    reportLayer.clearLayers();
    for (const report of args.reports) {
      const color = report.flags >= 3 ? '#b83f3f' : report.type === 'Free Parking' ? '#17674d' : '#bb760d';
      if (report.area) L.geoJSON(report.area, {style: {color, weight: 2, fillOpacity: .2}}).bindPopup(popup(report)).addTo(reportLayer);
      L.circleMarker([report.lat, report.lng], {radius: 7, color, fillOpacity: .8}).bindPopup(popup(report)).addTo(reportLayer);
    }
    lastReports = reportData;
  }
  const incoming = JSON.stringify(args.selection);
  if (incoming !== serverSelection) {
    serverSelection = incoming;
    if (args.selection && !point && !strokes.length) {
      if (args.selection.geometry) L.geoJSON(args.selection.geometry, {style: {color: '#17674d', fillOpacity: .4}}).addTo(draftLayer);
      else L.circleMarker([args.selection.lat, args.selection.lng], {radius: 9, color: '#17674d'}).addTo(draftLayer);
    }
  }
  map.invalidateSize();
  resize();
});
send('streamlit:componentReady', {apiVersion: 1});
resize();
