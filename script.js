/* ---------- MATRIX RAIN BACKGROUND ---------- */
const matrixCanvas = document.getElementById('matrixCanvas');
const mctx = matrixCanvas.getContext('2d');
let columns, drops;

function sizeMatrixCanvas() {
  matrixCanvas.width = window.innerWidth;
  matrixCanvas.height = window.innerHeight;
  columns = Math.floor(matrixCanvas.width / 16);
  drops = new Array(columns).fill(0);
}
sizeMatrixCanvas();
window.addEventListener('resize', sizeMatrixCanvas);

const glyphs = 'アイウエオカキクケコ01アイウエオ$#@!01'.split('');

function drawMatrix() {
  mctx.fillStyle = 'rgba(5, 8, 7, 0.08)';
  mctx.fillRect(0, 0, matrixCanvas.width, matrixCanvas.height);
  mctx.fillStyle = '#00ff66';
  mctx.font = '14px monospace';
  drops.forEach((y, i) => {
    const char = glyphs[Math.floor(Math.random() * glyphs.length)];
    mctx.fillText(char, i * 16, y);
    if (y > matrixCanvas.height && Math.random() > 0.975) drops[i] = 0;
    drops[i] += 16;
  });
}
setInterval(drawMatrix, 60);

/* ---------- BOOT SEQUENCE ---------- */
const bootLines = [
  '> initializing secure shell...',
  '> decrypting mainframe access...',
  '> loading identity: MARIB...',
  '> permissions: root granted.',
  '> welcome back.'
];
const bootText = document.getElementById('bootText');

function typeBootSequence(lineIndex = 0, charIndex = 0) {
  if (lineIndex >= bootLines.length) {
    setTimeout(() => {
      document.getElementById('boot').classList.add('hidden');
      document.getElementById('snapScreen').classList.remove('hidden');
      startAmbientParticles();
    }, 500);
    return;
  }
  const line = bootLines[lineIndex];
  bootText.textContent = bootLines.slice(0, lineIndex).join('\n') +
    (lineIndex > 0 ? '\n' : '') + line.slice(0, charIndex);

  if (charIndex < line.length) {
    setTimeout(() => typeBootSequence(lineIndex, charIndex + 1), 20);
  } else {
    setTimeout(() => typeBootSequence(lineIndex + 1, 0), 200);
  }
}
typeBootSequence();

/* ---------- AMBIENT PARTICLES ON THE SNAP SCREEN ---------- */
const snapCanvas = document.getElementById('snapParticles');
const sctx = snapCanvas.getContext('2d');
let ambientRunning = false;
let ambientDots = [];

function sizeSnapCanvas() {
  snapCanvas.width = window.innerWidth;
  snapCanvas.height = window.innerHeight;
}
sizeSnapCanvas();
window.addEventListener('resize', sizeSnapCanvas);

function startAmbientParticles() {
  if (ambientRunning) return;
  ambientRunning = true;
  ambientDots = Array.from({ length: 120 }, () => ({
    x: Math.random() * snapCanvas.width,
    y: Math.random() * snapCanvas.height,
    r: 0.8 + Math.random() * 2,
    vx: (Math.random() - 0.5) * 0.4,
    vy: (Math.random() - 0.5) * 0.4,
    a: 0.2 + Math.random() * 0.5
  }));

  function loop() {
    if (!ambientRunning) return;
    sctx.clearRect(0, 0, snapCanvas.width, snapCanvas.height);
    ambientDots.forEach(d => {
      d.x += d.vx;
      d.y += d.vy;
      if (d.x < 0) d.x = snapCanvas.width;
      if (d.x > snapCanvas.width) d.x = 0;
      if (d.y < 0) d.y = snapCanvas.height;
      if (d.y > snapCanvas.height) d.y = 0;
      sctx.beginPath();
      sctx.fillStyle = '#00ff66';
      sctx.globalAlpha = d.a;
      sctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
      sctx.fill();
    });
    sctx.globalAlpha = 1;
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
}

function stopAmbientParticles() {
  ambientRunning = false;
  sctx.clearRect(0, 0, snapCanvas.width, snapCanvas.height);
}

/* ---------- DUST / SNAP PARTICLE EFFECT ---------- */
const dustCanvas = document.getElementById('dustCanvas');
const dctx = dustCanvas.getContext('2d');

function sizeDustCanvas() {
  dustCanvas.width = window.innerWidth;
  dustCanvas.height = window.innerHeight;
}
sizeDustCanvas();
window.addEventListener('resize', sizeDustCanvas);

function burstParticles(duration, onPeak) {
  const count = 220;
  const particles = [];
  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * dustCanvas.width,
      y: Math.random() * dustCanvas.height,
      size: 1.5 + Math.random() * 3,
      vx: (Math.random() - 0.5) * 4,
      vy: -1 - Math.random() * 3,
      alpha: 1,
      color: Math.random() > 0.5 ? '#00ff66' : '#39ff9f'
    });
  }

  const start = performance.now();
  let peakFired = false;

  function frame(now) {
    const t = now - start;
    dctx.clearRect(0, 0, dustCanvas.width, dustCanvas.height);

    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.vy -= 0.01;
      p.alpha = Math.max(0, 1 - t / duration);
      dctx.fillStyle = p.color;
      dctx.globalAlpha = p.alpha;
      dctx.fillRect(p.x, p.y, p.size, p.size);
    });
    dctx.globalAlpha = 1;

    if (!peakFired && t > duration * 0.35) {
      peakFired = true;
      if (onPeak) onPeak();
    }

    if (t < duration) {
      requestAnimationFrame(frame);
    } else {
      dctx.clearRect(0, 0, dustCanvas.width, dustCanvas.height);
    }
  }
  requestAnimationFrame(frame);
}

/* ---------- SNAP BUTTON: intro -> main site ---------- */
const snapSound = document.getElementById('snapSound');

document.getElementById('snapBtn').addEventListener('click', () => {
  const snapScreen = document.getElementById('snapScreen');
  const site = document.getElementById('site');

  snapSound.currentTime = 0;
  snapSound.play().catch(() => {}); /* browsers can block autoplay-like calls; ignore if blocked */

  burstParticles(900, () => {
    snapScreen.style.transition = 'opacity 0.3s';
    snapScreen.style.opacity = '0';
  });

  setTimeout(() => {
    snapScreen.classList.add('hidden');
    site.classList.remove('hidden');
    stopAmbientParticles();
  }, 900);
});

/* ---------- NAV: switch sections with dust transition ---------- */
const navButtons = document.querySelectorAll('.nav-btn');
const pages = document.querySelectorAll('.page');
const speechBubble = document.getElementById('speechBubble');

const mascotLines = {
  home: "Yo. Welcome to my system — I'm Marib.",
  about: "This is my story, no fluff, just what I've actually built.",
  projects: "Here's what I've shipped so far. Take a look.",
  contact: "Got a problem worth solving? Let's talk."
};

function setActiveSection(target) {
  pages.forEach(p => p.classList.toggle('active', p.id === target));
  navButtons.forEach(b => b.classList.toggle('active', b.dataset.target === target));
  if (speechBubble && mascotLines[target]) {
    speechBubble.textContent = mascotLines[target];
  }
  window.scrollTo({ top: 0, behavior: 'instant' in window ? 'instant' : 'auto' });
}

navButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.target;
    const current = document.querySelector('.page.active');
    if (current && current.id === target) return;

    burstParticles(700, () => setActiveSection(target));
  });
});
