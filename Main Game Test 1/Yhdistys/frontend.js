document.addEventListener("DOMContentLoaded", (evt) => {
  evt.preventDefault()

  const form = document.getElementById("input-form")
  const input = document.getElementById("input")
  const terminal = document.getElementById("terminal")
  const taskButton = document.getElementById("task") // Get the button element
  const nextLevelButton = document.getElementById("next-level");
  let lastLevel = 0
  appendToTerminal("How to play:")
  appendToTerminal("Type 'task' or press button for task")
  appendToTerminal("You have 3 tries to answer correcty before losing hp")
  appendToTerminal("For answering question correctly you get coins")
  appendToTerminal("For answering question wrong something bad happens")
  appendToTerminal("After 5 tasks proceed to the next level by typing 'next level' or pressing button")
  appendToTerminal("To show stats type 'status'")
  appendToTerminal("To buy more hp type 'buy hp' (costs 3 coins)")
  appendToTerminal("If you forgor how to play, type '?' or 'help'")

  form.addEventListener("submit", async (event) => {
    event.preventDefault()
    const user_input = input.value.trim()
    if (!user_input) return

    appendToTerminal(`> ${user_input}`)
    input.value = "" //tyhjennä input field inputin jälkeen

    const response = await send_input(user_input) // odota api vastausta
    handle_response(response)
  })

  // napit nextLevel ja taskButton odottaa sen painamista
  taskButton.addEventListener("click", async () => {
    const response = await send_input("task")
    handle_response(response)
  })
  nextLevelButton.addEventListener("click", async () => {
    const response = await send_input("next level")
    handle_response(response)
  })
// lähettää inputin api:lle
  async function send_input(text) {
    try {
      const response = await fetch("http://localhost:5000/game", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({input: text})
      })
      const data = await response.json()
      return data
    } catch (error) {
      return {response: "To start the game, run api"}
    }
  }

  function handle_response(data) {
    if (!data.response) return

    // katsotaan että käsitellään tuleva data oikein
    if (typeof data.response === "object" && data.response.terminal) {
      appendToTerminal(data.response.terminal)

      if (data.response.latitude && data.response.longitude) {
        weatherUpdate(data.response.latitude, data.response.longitude)
      }

      if (data.response.currentLevel + 1 > lastLevel) {
        lastLevel = data.response.currentLevel
        highlightCountryByName(data.response.country)
        updateLevel(data.response.currentLevel)
      }
    } else {
      // If it's a plain string response
      appendToTerminal(data.response)
    }
  }
  function appendToTerminal(text) {
    terminal.innerHTML += `<div>${text}</div>`
    terminal.scrollTop = terminal.scrollHeight
  }
  // aika systeemi
  let secondsElapsed = 0;

  function formatTime(seconds) {
    const hours = String(Math.floor(seconds / 3600)).padStart(2, "0");
    const minutes = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
    const secs = String(seconds % 60).padStart(2, "0");
    return `${hours}:${minutes}:${secs}`;
  }

  function updateClock() {
    secondsElapsed++;
    const timeElement = document.getElementById("current-time");
    if (timeElement) {
      timeElement.textContent = formatTime(secondsElapsed);
    }
  }

// Start ticking every second
  setInterval(updateClock, 1000);
  updateClock();
})
document.getElementById("start-btn").addEventListener("click", () => {
    fetch("http://localhost:5000/start", { method: "POST" })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error("Error:", error));
});

document.getElementById("stop-btn").addEventListener("click", () => {
    fetch("http://localhost:5000/stop", { method: "POST" })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error("Error:", error));
});