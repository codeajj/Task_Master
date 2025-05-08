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
    input.value = "" // Reset input field

    const response = await send_input(user_input) // Wait for API response
    handle_response(response)
  })

  // Listen for "Next Task" button click
  taskButton.addEventListener("click", async () => {
    const response = await send_input("task") // Send the request for the next task
    handle_response(response)
  })
  nextLevelButton.addEventListener("click", async () => {
    const response = await send_input("next level") // Send the "next level" request
    handle_response(response)
  })

  async function send_input(text) {
    try {
      const response = await fetch("http://localhost:5000/game", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: text })
      })
      const data = await response.json()
      return data
    } catch (error) {
      return { response: "Error: Couldn't connect to server." }
    }
  }

  function handle_response(data) {
    if (!data.response) return

    // If the response has terminal info
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

})
