document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("input-form");
  const input = document.getElementById("input");
  const terminal = document.getElementById("terminal");
  const timerEl = document.getElementById("timer");
  const livesEl = document.getElementById("lives");
  const hintCountEl = document.getElementById("hints");
  const levelEl = document.getElementById("level");
  const levelNameEl = document.getElementById("level-name");
  const nextTaskBtn = document.getElementById("next-task");
  const nextLevelBtn = document.getElementById("next-level");

  let startTime = Date.now();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const userInput = input.value.trim();
    if (!userInput) return;

    appendToTerminal(`> ${userInput}`);
    input.value = "";

    const response = await sendInput(userInput);
    handleResponse(response);
  });

  nextTaskBtn.addEventListener("click", async () => {
    const response = await sendInput("next task");
    handleResponse(response);
  });

  nextLevelBtn.addEventListener("click", async () => {
    const response = await sendInput("next level");
    handleResponse(response);
  });

  async function sendInput(text) {
    try {
      const res = await fetch("http://localhost:5000/game", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: text })
      });

      const data = await res.json();
      return data;
    } catch (error) {
      return { response: "Error: Could not connect to server." };
    }
  }

  function handleResponse(data) {
    if (data.response) {
      appendToTerminal(data.response);
    }
    if (data.status) {
      updateStatus(data.status);
    }
  }

  function appendToTerminal(text) {
    terminal.innerHTML += `<div>${text}</div>`;
    terminal.scrollTop = terminal.scrollHeight;
  }

  function updateStatus(status) {
    if (status.time) timerEl.textContent = `Time: ${status.time}`;
    if (status.lives !== undefined) livesEl.textContent = `Lives: ${status.lives}`;
    if (status.hints !== undefined) hintCountEl.textContent = `Hints: ${status.hints}`;
    if (status.level !== undefined) levelEl.textContent = `Level: ${status.level + 1}`;
    if (status.country) levelNameEl.textContent = `Country: ${status.country}`;
    if (status.canAdvance) {
      nextLevelBtn.style.display = "inline-block";
    } else {
      nextLevelBtn.style.display = "none";
    }
  }

  setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const minutes = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const seconds = String(elapsed % 60).padStart(2, '0');
    timerEl.textContent = `Time: ${minutes}:${seconds}`;
  }, 1000);
});
