document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("input-form")
  const input = document.getElementById("input")
  const terminal = document.getElementById("terminal")

  form.addEventListener("submit", async (event) => {
    event.preventDefault()
    const user_input = input.value.trim()
    if (!user_input) return

    appendToTerminal(`> ${user_input}`)
    input.value = "";

    const response = await send_input(user_input)
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
    if (data.response) {
      appendToTerminal(data.response)
    }
  }

  function appendToTerminal(text) {
    terminal.innerHTML += `<div>${text}</div>`
    terminal.scrollTop = terminal.scrollHeight
  }

})
