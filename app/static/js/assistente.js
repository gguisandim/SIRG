document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("assistantForm");
  const input = document.getElementById("assistantInput");
  const messages = document.getElementById("assistantMessages");

  if (!form || !input || !messages) return;

  form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const pergunta = input.value.trim();

    if (!pergunta) return;

    adicionarMensagem("Você", pergunta, "user");
    input.value = "";

    adicionarMensagem("Assistente", "Pensando...", "bot loading");

    try {
      const response = await fetch("/assistente/perguntar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({ pergunta })
      });

      const data = await response.json();

      removerLoading();

      if (!response.ok) {
        adicionarMensagem("Assistente", data.erro || "Erro ao responder.", "bot");
        return;
      }

      adicionarMensagem("Assistente", data.resposta, "bot");

    } catch (error) {
      removerLoading();
      adicionarMensagem("Assistente", "Erro de conexão com o assistente.", "bot");
      console.error(error);
    }
  });

  function adicionarMensagem(autor, texto, classe) {
    const div = document.createElement("div");
    div.className = `assistant-message ${classe}`;
    div.innerHTML = `
      <strong>${autor}:</strong>
      <p>${texto}</p>
    `;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function removerLoading() {
    const loading = messages.querySelector(".loading");
    if (loading) loading.remove();
  }

  function getCSRFToken() {
    const token = document.querySelector('input[name="csrf_token"]');
    return token ? token.value : "";
  }
});