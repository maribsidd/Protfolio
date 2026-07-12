(function initCursor() {
  if (window.matchMedia("(hover: none), (pointer: coarse)").matches) return;

  const ring = document.createElement("div");
  ring.className = "cursor-ring";
  const dot = document.createElement("div");
  dot.className = "cursor-dot";
  document.body.appendChild(ring);
  document.body.appendChild(dot);

  let ringX = window.innerWidth / 2, ringY = window.innerHeight / 2;
  let mouseX = ringX, mouseY = ringY;

  window.addEventListener("mousemove", (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    dot.style.transform = `translate(${mouseX}px, ${mouseY}px) translate(-50%,-50%)`;
  });

  function loop() {
    ringX += (mouseX - ringX) * 0.16;
    ringY += (mouseY - ringY) * 0.16;
    ring.style.transform = `translate(${ringX}px, ${ringY}px) translate(-50%,-50%)`;
    requestAnimationFrame(loop);
  }
  loop();

  document.addEventListener("mouseover", (e) => {
    if (e.target.closest("a, button, .drop-zone, input, textarea, .menu-toggle")) {
      ring.classList.add("hovering");
    }
  });
  document.addEventListener("mouseout", (e) => {
    if (e.target.closest("a, button, .drop-zone, input, textarea, .menu-toggle")) {
      ring.classList.remove("hovering");
    }
  });

  document.addEventListener("click", (e) => {
    const splash = document.createElement("div");
    splash.className = "cursor-splash";
    splash.style.transform = `translate(${e.clientX}px, ${e.clientY}px) translate(-50%,-50%)`;
    document.body.appendChild(splash);
    setTimeout(() => splash.remove(), 650);
  });
})();
