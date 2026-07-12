async function loadStats() {
  const res = await fetch("/api/stats");
  const s = await res.json();
  document.getElementById("stat-scam-total").textContent = s.scam_scans_total;
  document.getElementById("stat-scam-high").textContent = s.high_risk_scams_flagged;
  document.getElementById("stat-cf-total").textContent = s.counterfeit_scans_total;
  document.getElementById("stat-rings").textContent = s.active_fraud_rings;
  document.getElementById("stat-cities").textContent = s.cities_monitored;
  document.getElementById("stat-incidents").textContent = s.total_incidents_30d;
}

function riskColor(risk) {
  if (risk === "high") return "#e1483f";
  if (risk === "medium") return "#f5a623";
  return "#2fbf9f";
}

async function loadNetwork() {
  const res = await fetch("/api/fraud-network");
  const data = await res.json();

  const nodes = new vis.DataSet(
    data.nodes.map((n) => ({
      id: n.id,
      label: n.label,
      color: { background: riskColor(n.risk), border: "#0b1220" },
      font: { color: "#eeeae1", size: 12, face: "IBM Plex Mono" },
      shape: n.group === "victim" ? "dot" : "box",
      size: 14,
    }))
  );
  const edges = new vis.DataSet(
    data.edges.map((e) => ({
      from: e.from,
      to: e.to,
      label: e.label,
      font: { color: "#6f7c93", size: 9, strokeWidth: 0 },
      color: { color: "#445066" },
      arrows: "to",
    }))
  );

  const container = document.getElementById("network-graph");
  new vis.Network(
    container,
    { nodes, edges },
    {
      physics: { stabilization: true, barnesHut: { gravitationalConstant: -4000, springLength: 120 } },
      interaction: { hover: true },
      nodes: { borderWidth: 1, shapeProperties: { borderRadius: 4 } },
    }
  );
}

async function loadMap() {
  const res = await fetch("/api/hotspots");
  const hotspots = await res.json();

  const map = L.map("map", { zoomControl: true, attributionControl: false }).setView([22.5, 79], 4.4);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    subdomains: "abcd",
    maxZoom: 19,
  }).addTo(map);

  const catColor = {
    digital_arrest: "#e1483f",
    upi_fraud: "#f5a623",
    phishing: "#8a7fd6",
    counterfeit: "#2fbf9f",
  };

  hotspots.forEach((h) => {
    const radius = 6 + (h.severity / 100) * 18;
    L.circleMarker([h.lat, h.lng], {
      radius,
      color: catColor[h.category] || "#f5a623",
      fillColor: catColor[h.category] || "#f5a623",
      fillOpacity: 0.45,
      weight: 1,
    })
      .addTo(map)
      .bindPopup(
        `<strong>${h.city}</strong><br>${h.category.replace("_", " ")}<br>Severity: ${h.severity}/100<br>${h.incidents_30d} incidents (30d)`
      );
  });
}

function badgeClass(verdict) {
  if (["CONFIRMED_SCAM_PATTERN", "LIKELY_COUNTERFEIT", "LIKELY_SCAM"].includes(verdict)) return "badge-danger";
  if (["SUSPICIOUS", "BE_CAUTIOUS"].includes(verdict)) return "badge-warn";
  return "badge-safe";
}

async function loadIncidents() {
  const res = await fetch("/api/recent-incidents");
  const items = await res.json();
  const body = document.getElementById("incident-body");
  if (!items.length) return;
  body.innerHTML = items
    .map(
      (i) => `<tr>
        <td>${i.type}</td>
        <td><span class="badge ${badgeClass(i.verdict)}">${i.verdict}</span></td>
        <td class="mono">${i.score}</td>
        <td class="mono">${i.time ? new Date(i.time).toLocaleString() : "—"}</td>
      </tr>`
    )
    .join("");
}

loadStats();
loadNetwork();
loadMap();
loadIncidents();
