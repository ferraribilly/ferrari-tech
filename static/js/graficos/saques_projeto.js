let acaoAtual = null;
let linhaAtual = null;

// 🔹 ABRIR MODAL
function abrirModal(acao, btn) {

  acaoAtual = acao;

  linhaAtual = btn.closest("tr");

  const modal = document.getElementById("modalSenha");

  if (modal) {

    modal.style.display = "flex";

  }

}

// 🔹 FECHAR MODAL
function fecharModal() {

  const modal = document.getElementById("modalSenha");

  if (modal) {

    modal.style.display = "none";

  }

  const senhaInput = document.getElementById("senhaInput");

  if (senhaInput) {

    senhaInput.value = "";

  }

}

// 🔹 CONFIRMAR
async function confirmarAcao() {

  const senhaInput = document.getElementById("senhaInput");

  const senha = senhaInput ? senhaInput.value.trim() : "";

  if (!senha) {

    return;

  }

  if (acaoAtual === "efetuandoSaque") {

    await efetuandoSaque(senha);

  }

}

// 🔹 SAQUE
async function efetuandoSaque(senha = "") {

  const linha = document.querySelector("#tabela-favorecido tr");

  if (!linha) {

    return;

  }

  const colunas = linha.querySelectorAll("td");

  // 🔥 IDENTIFICAÇÃO TEXTO NORMAL
  const identificacao =
    colunas[0].innerText.trim();

  // 🔥 INPUT VALOR
  const valor = parseFloat(

    (
      colunas[1].querySelector("input")?.value || "0"
    ).replace(",", ".")

  ) || 0;

  // 🔥 INPUT DESCRIÇÃO
  const descricao =
    colunas[2].querySelector("input")?.value.trim() || "";

  // 🔥 TEXTO NORMAL
  const nome = colunas[3].innerText.trim();

  const cpf = colunas[4].innerText.trim();

  const email = colunas[5].innerText.trim();

  const status = colunas[6].innerText.trim();

  if (!identificacao || !valor || !cpf) {

    return;

  }

  const payload = {

    identificacao,

    valor_unidade: valor,

    descricao,

    nome_favorecido: nome,

    cpf_favorecido: cpf,

    email_favorecido: email,

    status,

    senha

  };

  // 🔹 FECHA MODAL AQUI
  fecharModal();

  // 🔹 Overlay de carregamento
  const overlay = document.createElement("div");

  overlay.id = "overlay-processando";

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

    <div style="color:#fff; font-size:22px; font-family:monospace;">

      Processando saque... Aguarde...

      <br><br>

      <div class="loader"></div>

    </div>

  `;

  document.body.appendChild(overlay);

  // 🔹 Loader CSS
  const style = document.createElement("style");

  style.innerHTML = `

    .loader {

      border: 6px solid #f3f3f3;

      border-top: 6px solid #3498db;

      border-radius: 50%;

      width: 40px;

      height: 40px;

      animation: spin 1s linear infinite;

      margin: auto;

    }

    @keyframes spin {

      0% {

        transform: rotate(0deg);

      }

      100% {

        transform: rotate(360deg);

      }

    }

  `;

  document.head.appendChild(style);

  try {

    await fetch("/saques_projeto", {

      method: "POST",

      headers: {

        "Content-Type": "application/json"

      },

      body: JSON.stringify(payload)

    });

    setTimeout(() => {

      location.reload();

    }, 2000);

  } catch (err) {

    console.error(err);

    setTimeout(() => {

      location.reload();

    }, 2000);

  }

}