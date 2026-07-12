function verdictColor(v) {
  if (v === "CONFIRMED_SCAM_PATTERN") return "var(--danger)";
  if (v === "LIKELY_SCAM") return "var(--danger)";
  if (v === "SUSPICIOUS") return "var(--amber)";
  if (v === "ERROR") return "var(--steel)";
  return "var(--safe)";
}

function renderVerdict(result) {
  const box = document.getElementById("verdict-box");
  box.classList.add("show");
  document.getElementById("verdict-label").textContent = "Verdict: " + result.verdict;
  const scoreEl = document.getElementById("verdict-score");
  scoreEl.textContent = result.risk_score + " / 100";
  scoreEl.style.color = verdictColor(result.verdict);
  document.getElementById("verdict-reasoning").textContent = result.reasoning || "";
  const list = document.getElementById("flag-list");
  list.innerHTML = (result.red_flags || []).map((f) => `<li>${f}</li>`).join("");
  box.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function renderAgentTrace(fusionResult) {
  const panel = document.getElementById("agent-trace-panel");
  panel.style.display = "block";
  document.getElementById("matched-count").textContent =
    (fusionResult.correlation?.matched_nodes || []).length;
  document.getElementById("agent-report-text").textContent =
    fusionResult.report?.incident_report || "No report generated.";
}

async function analyzeTranscript(transcript) {
  const res = await fetch("/api/agent-fusion", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ transcript }),
  });
  return res.json();
}

document.getElementById("analyze-btn").addEventListener("click", async () => {
  const btn = document.getElementById("analyze-btn");
  const text = document.getElementById("transcript-input").value.trim();
  if (!text) return;
  btn.textContent = "Analyzing...";
  btn.disabled = true;
  try {
    const fusion = await analyzeTranscript(text);
    renderVerdict(fusion.detection);
    renderAgentTrace(fusion);
  } finally {
    btn.textContent = "Analyze transcript";
    btn.disabled = false;
  }
});

document.getElementById("clear-btn").addEventListener("click", () => {
  document.getElementById("transcript-input").value = "";
});

document.getElementById("run-demo-btn").addEventListener("click", async () => {
  const btn = document.getElementById("run-demo-btn");
  const container = document.getElementById("live-transcript");
  btn.disabled = true;
  btn.textContent = "Running...";
  container.innerHTML = "";

  const res = await fetch("/api/scam-demo-script");
  const { lines } = await res.json();

  for (const line of lines) {
    const div = document.createElement("div");
    div.className = "transcript-line";
    div.textContent = line;
    container.appendChild(div);
    await new Promise((r) => setTimeout(r, 60));
    div.classList.add("shown");
    await new Promise((r) => setTimeout(r, 700));
  }

  const fullTranscript = lines.join("\n");
  btn.textContent = "Scoring call...";
  try {
    const fusion = await analyzeTranscript(fullTranscript);
    renderVerdict(fusion.detection);
    renderAgentTrace(fusion);
  } finally {
    btn.textContent = "Run simulated call";
    btn.disabled = false;
  }
});
