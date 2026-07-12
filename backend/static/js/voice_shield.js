const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const fileName = document.getElementById("file-name");
const analyzeBtn = document.getElementById("analyze-btn");
let selectedFile = null;

document.getElementById("drop-zone").addEventListener("click", () => fileInput.click());
dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("dragover"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener("change", (e) => {
  if (e.target.files.length) handleFile(e.target.files[0]);
});

function handleFile(file) {
  if (!file.type.startsWith("audio/")) return;
  selectedFile = file;
  fileName.textContent = file.name;
  analyzeBtn.disabled = false;
}

function verdictColor(v) {
  if (v === "CONFIRMED_SCAM_PATTERN" || v === "LIKELY_SCAM") return "var(--danger)";
  if (v === "SUSPICIOUS") return "var(--amber)";
  if (v === "ERROR") return "var(--steel)";
  return "var(--safe)";
}

analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) return;
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Transcribing...";

  const formData = new FormData();
  formData.append("audio", selectedFile);

  try {
    const res = await fetch("/api/voice-detect", { method: "POST", body: formData });
    const result = await res.json();

    if (result.transcript) {
      document.getElementById("transcript-panel").style.display = "block";
      document.getElementById("transcript-text").textContent = result.transcript;
    }

    const box = document.getElementById("verdict-box");
    box.classList.add("show");
    document.getElementById("verdict-label").textContent = "Verdict: " + result.verdict;
    const scoreEl = document.getElementById("verdict-score");
    scoreEl.textContent = (result.risk_score ?? 0) + " / 100";
    scoreEl.style.color = verdictColor(result.verdict);
    document.getElementById("verdict-reasoning").textContent = result.reasoning || "";
    document.getElementById("flag-list").innerHTML = (result.red_flags || []).map((f) => `<li>${f}</li>`).join("");
    box.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Transcribe & analyze";
  }
});
