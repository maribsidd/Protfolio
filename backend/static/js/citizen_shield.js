const chatWindow = document.getElementById("chat-window");
const chatInput = document.getElementById("chat-input");
const chatSend = document.getElementById("chat-send");

function addBubble(text, who) {
  const div = document.createElement("div");
  div.className = "chat-bubble " + who;
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return div;
}

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;
  addBubble(text, "user");
  chatInput.value = "";
  chatSend.disabled = true;
  const thinking = addBubble("Thinking...", "bot");

  try {
    const res = await fetch("/api/citizen-chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const result = await res.json();
    thinking.textContent = result.reply;
    if (result.verdict === "LIKELY_SCAM") {
      thinking.style.borderColor = "var(--danger)";
    } else if (result.verdict === "BE_CAUTIOUS") {
      thinking.style.borderColor = "var(--amber)";
    }
  } catch (e) {
    thinking.textContent = "Something went wrong reaching the detection engine. Please try again.";
  } finally {
    chatSend.disabled = false;
  }
}

chatSend.addEventListener("click", sendMessage);
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});
