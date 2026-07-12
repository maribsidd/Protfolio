const draftBtn = document.getElementById("draft-btn");
const output = document.getElementById("draft-output");
const copyBtn = document.getElementById("copy-btn");

draftBtn.addEventListener("click", async () => {
  const incident_type = document.getElementById("incident-type").value;
  const incident_date = document.getElementById("incident-date").value.trim();
  const amount_lost = document.getElementById("amount-lost").value.trim();
  const description = document.getElementById("description").value.trim();
  const perpetrator_details = document.getElementById("perpetrator-details").value.trim();

  if (!description) {
    output.textContent = "Please describe what happened before generating a draft.";
    return;
  }

  draftBtn.disabled = true;
  draftBtn.textContent = "Drafting...";
  output.textContent = "Generating your complaint draft...";

  try {
    const res = await fetch("/api/complaint-draft", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ incident_type, incident_date, amount_lost, description, perpetrator_details }),
    });
    const result = await res.json();
    output.textContent = result.draft_text || "Something went wrong generating the draft.";
  } finally {
    draftBtn.disabled = false;
    draftBtn.textContent = "Generate draft";
  }
});

copyBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(output.textContent).then(() => {
    copyBtn.textContent = "Copied!";
    setTimeout(() => { copyBtn.textContent = "Copy draft"; }, 1500);
  });
});
