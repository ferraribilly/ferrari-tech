let redeSelecionada = "";

function abrirCardLink() {
  const select = document.getElementById("select_rede");
  const card = document.getElementById("card_link");

  redeSelecionada = select.value;

  if (redeSelecionada) {
    card.style.display = "block";
  }
}

function confirmarLink() {
  const input = document.getElementById("input_link");
  const lista = document.getElementById("lista_links");

  if (!redeSelecionada || !input.value) return;

  const div = document.createElement("div");
  div.innerHTML = `
    <b>${redeSelecionada}:</b>
    <a href="${input.value}" target="_blank">${input.value}</a>
    <br>
  `;

  lista.appendChild(div);

  // reset
  document.getElementById("select_rede").value = "";
  document.getElementById("card_link").style.display = "none";
  input.value = "";
  redeSelecionada = "";
}