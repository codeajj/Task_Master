document.addEventListener("DOMContentLoaded", (evt) => {
  evt.preventDefault()
  const form = document.getElementById("input-form")
  const input = document.getElementById("input")
  const terminal = document.getElementById("terminal")
  let lastLevel =0
  form.addEventListener("submit", async (event) => {
    event.preventDefault()
    const user_input = input.value.trim()
    if (!user_input) return

    appendToTerminal(`> ${user_input}`)
    input.value = ""; // jos input tyhjä ei tehdä mitään

    const response = await send_input(user_input) // Vastauksen odotus
    handle_response(response)
  })

  async function send_input(text) { // Koko pää skeida jolla nyt tehdää API call ja saadaan tieto revittyy.
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

  // If it's an object with 'terminal'
  if (typeof data.response === "object" && data.response.terminal) {
    appendToTerminal(data.response.terminal)

    if (data.response.latitude && data.response.longitude) {
      weatherUpdate(data.response.latitude, data.response.longitude)
    }

    if (data.response.currentLevel > lastLevel) {
      lastLevel = data.response.currentLevel
      highlightCountryByName(data.response.country)
    }
  } else {
    // It's a plain string response
    appendToTerminal(data.response)
  }
}


  function appendToTerminal(text) { // Ei tyhjän inputin lisäys terminaaliin + scroll
    terminal.innerHTML += `<div>${text}</div>`
    terminal.scrollTop = terminal.scrollHeight
  }

})
