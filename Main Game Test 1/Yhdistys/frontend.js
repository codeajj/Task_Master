document.addEventListener("DOMContentLoaded", (evt) => {
  evt.preventDefault()

  const form = document.getElementById("input-form")
  const input = document.getElementById("input")
  const terminal = document.getElementById("terminal")
  const taskButton = document.getElementById("task") // Get the button element
  const nextLevelButton = document.getElementById("next-level");
  let lastLevel = 0

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
      return {response: "Error: Couldn't connect to server."}
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