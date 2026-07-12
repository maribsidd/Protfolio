let allCards = [];

function catLabel(cat) {
  const labels = { digital_arrest: "Digital Arrest", upi_fraud: "UPI Fraud", counterfeit: "Counterfeit", policy: "Policy & Law" };
  return labels[cat] || cat;
}

function renderCards(cards) {
  const grid = document.getElementById("news-grid");
  if (!cards.length) {
    grid.innerHTML = `<p class="mono" style="color:var(--paper-dim)">No stories in this category yet.</p>`;
    return;
  }
  grid.innerHTML = cards.map((c) => `
    <div class="news-card">
      <span class="news-cat cat-${c.category}">${catLabel(c.category)}</span>
      <h3>${c.headline}</h3>
      <p>${c.summary}</p>
      <div class="news-meta">
        <span>${c.publisher} · ${c.published_on}</span>
        <a href="${c.url}" target="_blank" rel="noopener">Read full story →</a>
      </div>
    </div>
  `).join("");
}

async function loadNews() {
  const res = await fetch("/api/news-cards");
  allCards = await res.json();
  renderCards(allCards);
}

document.getElementById("filter-row").addEventListener("click", (e) => {
  const btn = e.target.closest(".filter-chip");
  if (!btn) return;
  document.querySelectorAll(".filter-chip").forEach((c) => c.classList.remove("active"));
  btn.classList.add("active");
  const cat = btn.dataset.cat;
  renderCards(cat === "all" ? allCards : allCards.filter((c) => c.category === cat));
});

loadNews();
