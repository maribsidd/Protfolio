/* ---------- Three.js radar-sentinel hero ---------- */
(function initRadarHero() {
  const canvas = document.getElementById("hero-canvas");
  if (!canvas || typeof THREE === "undefined") return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 0, 9);

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  const group = new THREE.Group();
  scene.add(group);

  // Concentric radar rings
  const ringColor = 0x445066;
  const amberColor = 0xf5a623;
  for (let i = 1; i <= 4; i++) {
    const geo = new THREE.RingGeometry(i * 1.05 - 0.008, i * 1.05, 128);
    const mat = new THREE.MeshBasicMaterial({ color: ringColor, transparent: true, opacity: 0.35, side: THREE.DoubleSide });
    const ring = new THREE.Mesh(geo, mat);
    group.add(ring);
  }

  // Radial guide lines
  const lineMat = new THREE.LineBasicMaterial({ color: ringColor, transparent: true, opacity: 0.25 });
  for (let a = 0; a < 8; a++) {
    const angle = (a / 8) * Math.PI * 2;
    const points = [
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(Math.cos(angle) * 4.3, Math.sin(angle) * 4.3, 0),
    ];
    const geo = new THREE.BufferGeometry().setFromPoints(points);
    group.add(new THREE.Line(geo, lineMat));
  }

  // Sweep wedge (radial-gradient texture on a plane, rotated each frame)
  function makeSweepTexture() {
    const size = 512;
    const c = document.createElement("canvas");
    c.width = c.height = size;
    const ctx = c.getContext("2d");
    const grad = ctx.createConicGradient
      ? ctx.createConicGradient(-Math.PI / 2, size / 2, size / 2)
      : null;
    if (grad) {
      grad.addColorStop(0, "rgba(245,166,35,0.55)");
      grad.addColorStop(0.06, "rgba(245,166,35,0.18)");
      grad.addColorStop(0.14, "rgba(245,166,35,0)");
      grad.addColorStop(1, "rgba(245,166,35,0)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, size, size);
    } else {
      ctx.fillStyle = "rgba(245,166,35,0.2)";
      ctx.fillRect(0, 0, size, size);
    }
    return new THREE.CanvasTexture(c);
  }
  const sweepTex = makeSweepTexture();
  const sweepMat = new THREE.MeshBasicMaterial({ map: sweepTex, transparent: true, depthWrite: false });
  const sweepMesh = new THREE.Mesh(new THREE.PlaneGeometry(8.6, 8.6), sweepMat);
  sweepMesh.position.z = 0.01;
  group.add(sweepMesh);

  // Sentinel core (center glyph)
  const coreGeo = new THREE.IcosahedronGeometry(0.42, 1);
  const coreMat = new THREE.MeshBasicMaterial({ color: amberColor, wireframe: true, transparent: true, opacity: 0.9 });
  const core = new THREE.Mesh(coreGeo, coreMat);
  group.add(core);

  // Blips: random points around rings that pulse
  const blips = [];
  const blipGeo = new THREE.CircleGeometry(0.045, 16);
  for (let i = 0; i < 9; i++) {
    const ringR = [1.05, 2.1, 3.15, 4.2][Math.floor(Math.random() * 4)];
    const angle = Math.random() * Math.PI * 2;
    const isDanger = Math.random() < 0.35;
    const mat = new THREE.MeshBasicMaterial({
      color: isDanger ? 0xe1483f : 0x2fbf9f,
      transparent: true,
      opacity: 0,
    });
    const blip = new THREE.Mesh(blipGeo, mat);
    blip.position.set(Math.cos(angle) * ringR, Math.sin(angle) * ringR, 0.02);
    blip.userData = { angle, ringR, delay: Math.random() * 6, danger: isDanger };
    group.add(blip);
    blips.push(blip);
  }

  group.rotation.x = 0.15;

  function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }
  window.addEventListener("resize", onResize);

  const clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();
    sweepMesh.rotation.z = -t * 0.6;
    core.rotation.x = t * 0.3;
    core.rotation.y = t * 0.4;
    group.rotation.y = Math.sin(t * 0.08) * 0.12;

    const sweepAngle = ((-t * 0.6) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2);
    blips.forEach((b) => {
      const diff = Math.abs(((b.userData.angle - sweepAngle + Math.PI * 3) % (Math.PI * 2)) - Math.PI);
      const proximity = 1 - Math.min(diff / 0.5, 1);
      if (proximity > 0) {
        b.material.opacity = Math.max(b.material.opacity, proximity * 0.95);
      }
      b.material.opacity *= 0.965;
    });

    renderer.render(scene, camera);
  }
  animate();
})();

/* ---------- GSAP scroll reveals + marquee ---------- */
window.addEventListener("DOMContentLoaded", () => {
  if (typeof gsap === "undefined") return;
  gsap.registerPlugin(ScrollTrigger);

  gsap.utils.toArray(".reveal").forEach((el) => {
    gsap.to(el, {
      opacity: 1,
      y: 0,
      duration: 0.9,
      ease: "power3.out",
      scrollTrigger: { trigger: el, start: "top 85%" },
    });
  });

  gsap.from(".hero-content > *", {
    opacity: 0,
    y: 24,
    duration: 1,
    stagger: 0.12,
    ease: "power3.out",
    delay: 0.2,
  });

  // Duplicate marquee track content for seamless loop
  const track = document.querySelector(".marquee-track");
  if (track) {
    track.insertAdjacentHTML("afterend", `<div class="marquee-track">${track.innerHTML}</div>`);
    const tracks = document.querySelectorAll(".marquee-track");
    gsap.to(tracks, { xPercent: -100, repeat: -1, duration: 26, ease: "linear" });
  }
});
