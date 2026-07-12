const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const previewImg = document.getElementById("preview-img");
const scanBtn = document.getElementById("scan-btn");
let selectedFile = null;

dropZone.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});
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
  if (!file.type.startsWith("image/")) return;
  selectedFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    previewImg.style.display = "block";
  };
  reader.readAsDataURL(file);
  scanBtn.disabled = false;
}

function verdictColor(v) {
  if (v === "LIKELY_COUNTERFEIT") return "var(--danger)";
  if (v === "SUSPICIOUS") return "var(--amber)";
  if (v === "NOT_APPLICABLE") return "var(--steel)";
  if (v === "ERROR") return "var(--steel)";
  return "var(--safe)";
}

function renderVerdict(result) {
  const box = document.getElementById("verdict-box");
  box.classList.add("show");
  let label = "Verdict: " + result.verdict;
  if (result.verdict === "NOT_APPLICABLE" && result.currency_type === "non_INR") {
    label = "Not an Indian note \u2014 authentication not supported yet";
  }
  label += result.denomination_guess ? " \u00b7 " + result.denomination_guess : "";
  document.getElementById("verdict-label").textContent = label;
  const scoreEl = document.getElementById("verdict-score");
  scoreEl.textContent = result.verdict === "NOT_APPLICABLE"
    ? result.confidence + "% identification confidence"
    : result.confidence + "% confidence";
  scoreEl.style.color = verdictColor(result.verdict);
  document.getElementById("verdict-reasoning").textContent = result.reasoning || "";
  const list = document.getElementById("flag-list");
  list.innerHTML = (result.flagged_features || []).map((f) => `<li>${f}</li>`).join("");
  box.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

scanBtn.addEventListener("click", async () => {
  if (!selectedFile) return;
  scanBtn.disabled = true;
  scanBtn.textContent = "Scanning...";
  const formData = new FormData();
  formData.append("image", selectedFile);
  try {
    const res = await fetch("/api/counterfeit-detect", { method: "POST", body: formData });
    const result = await res.json();
    renderVerdict(result);
  } finally {
    scanBtn.disabled = false;
    scanBtn.textContent = "Scan note";
  }
});
