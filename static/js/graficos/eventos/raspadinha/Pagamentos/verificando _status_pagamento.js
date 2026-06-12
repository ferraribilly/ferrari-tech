function verificarStatus() {
  const statusEl = document.getElementById("status");
  const paymentIdEl = document.getElementById("payment_id");
  const usuarioEl = document.getElementById("usuario-id"); // PEGA PELO ID

  if (!statusEl || !paymentIdEl || !usuarioEl) return;

  const status = statusEl.textContent.trim().toLowerCase();
  const payment_id = paymentIdEl.textContent.trim();
  const usuario_id = usuarioEl.textContent.trim(); // PEGA O VALOR DO TEXTO

  if (status === "approved") {
    fetch("/sync_raspadinhas_aprovados", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ payment_id: payment_id }),
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("Raspadinhas atualizados:", data);
        if (data.ok === true) {
          sessionStorage.setItem("usuario_id", usuario_id); // SALVA CERTO
          window.location.href = "/success";
        }
      })
      .catch((err) => console.error("Erro:", err));
  }
}

verificarStatus();
setInterval(verificarStatus, 2000);

document.addEventListener("visibilitychange", function () {
  if (!document.hidden) verificarStatus();
});

window.addEventListener("focus", verificarStatus);

// Roda de 2 em 2 segundos
setInterval(verificarStatus, 2000);

// 👇 ISSO AQUI QUE RESOLVE O PROBLEMA DE VOLTAR PARA A PÁGINA
document.addEventListener("visibilitychange", function () {
  if (!document.hidden) {
    console.log("Usuário voltou para a página, verificando...");
    verificarStatus(); // Verifica na hora que volta
  }
});

// E também quando a janela ganha foco de novo
window.addEventListener("focus", verificarStatus);

document.getElementById("copy").addEventListener("click", copyText);
// document.getElementById('copy-mobile').addEventListener('click', copyText);

function copyText() {
  var qrcodeText = document.getElementById("qrcode-text");
  var copiedCodeBox = document.getElementById("copied-code");

  navigator.clipboard.writeText(qrcodeText.textContent).then(
    function () {
      // Efeito de blur e mostrar mensagem
      qrcodeText.style.filter = "blur(1px)";
      copiedCodeBox.style.visibility = "visible";
      copiedCodeBox.style.opacity = "0.9";
      copiedCodeBox.style.transition = "all 0.3s";

      setTimeout(function () {
        qrcodeText.style.filter = "";
        copiedCodeBox.style.visibility = "";
        copiedCodeBox.style.opacity = "";
      }, 5000);
    },
    function (err) {
      console.error("Erro ao copiar: ", err);
    },
  );
}
