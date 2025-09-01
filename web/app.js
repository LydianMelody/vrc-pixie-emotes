const $ = (sel) => document.querySelector(sel);
const log = (m) => { const el = $('#log'); el.textContent += `${m}\n`; el.scrollTop = el.scrollHeight; };

const paths = { originalAnim: null, originalStill: null, sprite: null };
let currentTab = 'original';
let playing = false;
let frameImages = [];
let frameDurations = [];
let frameIndex = 0;
let playTimer = null;

function setTab(name) {
  currentTab = name;
  document.querySelectorAll('.tab').forEach(t => {
    t.classList.toggle('tab--active', t.dataset.tab === name);
  });
  // Toggle help visibility
  const helpEl = document.getElementById('help');
  if (helpEl) helpEl.hidden = name !== 'help';
  const previewArea = document.getElementById('preview-area');
  if (name === 'original') {
    if (previewArea) previewArea.style.display = 'block';
    if (frameImages.length) {
      // Use canvas player
      $('#preview-image').style.display = 'none';
      $('#player').style.display = 'block';
      $('#placeholder').style.display = 'none';
      drawFrame();
    } else {
      // Fallback to image-based preview
      $('#player').style.display = 'none';
      const hasSrc = Boolean(paths.originalAnim || paths.originalStill);
      $('#preview-image').style.display = hasSrc ? 'block' : 'none';
      $('#placeholder').style.display = hasSrc ? 'none' : 'grid';
      const src = playing && paths.originalAnim ? paths.originalAnim : paths.originalStill || paths.originalAnim;
      if (src) $('#preview-image').src = src + `?t=${Date.now()}`;
    }
  } else if (name === 'sprite') {
    if (previewArea) previewArea.style.display = 'block';
    if (paths.sprite) $('#preview-image').src = paths.sprite + `?t=${Date.now()}`;
    $('#player').style.display = 'none';
    $('#preview-image').style.display = 'block';
    $('#placeholder').style.display = paths.sprite ? 'none' : 'grid';
  } else if (name === 'help') {
    // Hide preview area entirely on Help tab
    if (previewArea) previewArea.style.display = 'none';
    $('#player').style.display = 'none';
    $('#preview-image').style.display = 'none';
    $('#placeholder').style.display = 'none';
  }
  drawChecker();
}

// Draw checkerboard
function drawChecker() {
  const c = document.getElementById('checker');
  const d = c.getContext('2d');
  const rect = c.parentElement.getBoundingClientRect();
  c.width = rect.width; c.height = rect.height;
  const tile = 24, a = '#fff6fb', b = '#f2f8ff';
  for (let y = 0; y < c.height; y += tile) {
    for (let x = 0; x < c.width; x += tile) {
      d.fillStyle = ((x / tile + y / tile) % 2 === 0) ? a : b;
      d.fillRect(x, y, tile, tile);
    }
  }
}

window.addEventListener('resize', drawChecker);
document.addEventListener('DOMContentLoaded', () => {
  drawChecker();
  document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => setTab(t.dataset.tab)));
  // Nothing to toggle now; single remove-every pattern input is always visible
  // Simple tooltip writer
  const tips = $('#tips');
  document.body.addEventListener('mouseover', (e) => {
    const tip = e.target && e.target.getAttribute && e.target.getAttribute('data-tip');
    if (tip && tips) { tips.textContent = tip; }
  });
  document.body.addEventListener('mouseout', (e) => {
    const tip = e.target && e.target.getAttribute && e.target.getAttribute('data-tip');
    if (tip && tips) { tips.textContent = ''; }
  });
  // Drag & drop upload
  const preview = document.querySelector('.preview');
  preview.addEventListener('dragover', (e) => { e.preventDefault(); preview.classList.add('dragover'); });
  preview.addEventListener('dragleave', () => preview.classList.remove('dragover'));
  preview.addEventListener('drop', async (e) => {
    e.preventDefault(); preview.classList.remove('dragover');
    const file = e.dataTransfer.files && e.dataTransfer.files[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.gif')) { log('Please drop a .gif file'); return; }
    log(`Importing dropped file: ${file.name}`);
    const arrayBuffer = await file.arrayBuffer();
    const bytes = new Uint8Array(arrayBuffer);
    // Convert to base64
    let binary = ''; for (let i = 0; i < bytes.byteLength; i++) { binary += String.fromCharCode(bytes[i]); }
    const b64 = btoa(binary);
    const info = await eel.import_gif_bytes(b64, file.name)();
    await handleGifInfo(info);
  });
});

$('#btn-browse').addEventListener('click', async () => {
  log('Opening file dialog…');
  try {
    const path = await eel.open_file_dialog()();
    if (!path) return;
    log(`Loading GIF: ${path}`);
    const info = await eel.load_gif(path)();
    await handleGifInfo(info);
    log(`Frames: ${info.total_frames}, Size: ${info.original_dimensions[0]}x${info.original_dimensions[1]}`);
  } catch (e) {
    log(`Error: ${e}`);
  }
});

async function handleGifInfo(info) {
  if (!info) return;
  paths.originalAnim = info.original_preview_path || null;
  paths.originalStill = info.preview_path || null;
  playing = false; setPlayIcon();
  if (info.frames && info.frames.length) {
    await preloadFrames(info.frames);
  } else {
    frameImages = []; frameDurations = []; frameIndex = 0;
  }
  $('#placeholder').style.display = 'none';
  setTab('original');
}

function setPlayIcon() {
  const btn = document.getElementById('btn-play');
  btn.textContent = playing ? '⏸' : '▶';
  btn.title = playing ? 'Pause' : 'Play';
}

function startPlayback() {
  if (currentTab !== 'original') return;
  playing = true; setPlayIcon();
  if (frameImages.length) {
    $('#preview-image').style.display = 'none';
    $('#player').style.display = 'block';
    scheduleNextTick(0);
  } else {
    const src = paths.originalAnim || paths.originalStill;
    if (src) $('#preview-image').src = src + `?t=${Date.now()}`;
  }
}

function pausePlayback() {
  playing = false; setPlayIcon();
  if (playTimer) { clearTimeout(playTimer); playTimer = null; }
  if (!frameImages.length && paths.originalStill) {
    // Fallback: show still when not using canvas frames
    document.getElementById('preview-image').src = paths.originalStill + `?t=${Date.now()}`;
  } else {
    // Canvas already shows the last drawn frame -> freeze
    drawFrame();
  }
}

function stopPlayback() {
  playing = false; setPlayIcon();
  if (playTimer) { clearTimeout(playTimer); playTimer = null; }
  frameIndex = 0;
  if (frameImages.length) {
    $('#preview-image').style.display = 'none';
    $('#player').style.display = 'block';
    drawFrame();
  } else if (paths.originalStill) {
    document.getElementById('preview-image').src = paths.originalStill + `?t=${Date.now()}`;
  }
}

document.getElementById('btn-play').addEventListener('click', () => {
  if (playing) { pausePlayback(); } else { startPlayback(); }
});

$('#btn-stop').addEventListener('click', stopPlayback);

$('#btn-generate').addEventListener('click', async () => {
  log('Generating sprite sheet…');
  const settings = {
    optimize: $('#optimize').checked,
    maxColors: parseInt($('#maxColors').value, 10) || 256,
    fps: parseInt($('#fps').value, 10) || 10,
    removeEvery: parseInt(document.getElementById('removeEvery').value, 10) || 0,
  };
  try {
    const res = await eel.generate_sprite_sheet(settings)();
    if (res && res.preview_path) {
      paths.sprite = res.preview_path;
      setTab('sprite');
    }
    log(res.message || 'Done');
  } catch (e) {
    log(`Error: ${e}`);
  }
});

$('#btn-save').addEventListener('click', async () => {
  try {
    const res = await eel.save_sprite_sheet()();
    log(res.message || 'Save complete');
  } catch (e) {
    log(`Error: ${e}`);
  }
});

function drawFrame() {
  const canvas = document.getElementById('player');
  const ctx = canvas.getContext('2d');
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width; canvas.height = rect.height;
  const img = frameImages[frameIndex];
  if (!img) return;
  const scale = Math.min(canvas.width / img.width, canvas.height / img.height);
  const w = Math.max(1, Math.floor(img.width * scale));
  const h = Math.max(1, Math.floor(img.height * scale));
  const x = Math.floor((canvas.width - w) / 2);
  const y = Math.floor((canvas.height - h) / 2);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(img, x, y, w, h);
}

function scheduleNextTick(initialDelay) {
  if (!playing) return;
  const delay = initialDelay ?? Math.max(20, frameDurations[frameIndex] || 100);
  playTimer = setTimeout(() => {
    if (!playing) return;
    drawFrame();
    const d = Math.max(20, frameDurations[frameIndex] || 100);
    frameIndex = (frameIndex + 1) % frameImages.length;
    scheduleNextTick(d);
  }, delay);
}

async function preloadFrames(metaFrames) {
  frameImages = [];
  frameDurations = metaFrames.map(f => Math.max(20, f.duration || 100));
  frameIndex = 0;
  const promises = metaFrames.map(f => new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.src = f.path + `?t=${Date.now()}`;
  }));
  frameImages = await Promise.all(promises);
}
