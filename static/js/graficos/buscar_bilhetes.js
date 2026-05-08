function buscarDados() {
  const valor = document.getElementById("dados-filter").value;

  // 🔹 overlay de busca
  const overlay = document.createElement("div");
  overlay.id = "overlay-busca";
  overlay.style.position = "fixed";
  overlay.style.top = "0";
  overlay.style.left = "0";
  overlay.style.width = "100%";
  overlay.style.height = "100%";
  overlay.style.background = "rgba(0,0,0,0.6)";
  overlay.style.display = "flex";
  overlay.style.alignItems = "center";
  overlay.style.justifyContent = "center";
  overlay.style.zIndex = "9999";

  overlay.innerHTML = `
    <div style="color:#fff; font-size:22px; font-family:monospace; text-align:center;">
      Buscando bilhetes...
      <br><br>
      <div class="loader"></div>
    </div>
  `;

  document.body.appendChild(overlay);

  // 🔹 redireciona
  setTimeout(() => {
    window.location.href = "/controle_vendas?q=" + encodeURIComponent(valor);
  }, 300);
}