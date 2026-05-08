let acaoAtual = null;
let linhaAtual = null;

// 🔹 ABRIR MODAL
function abrirModal(acao, btn) {
  acaoAtual = acao;
  linhaAtual = btn.closest("tr");
  document.getElementById("modalSenha").style.display = "flex";
}

// 🔹 FECHAR MODAL
function fecharModal() {
  document.getElementById("modalSenha").style.display = "none";
  document.getElementById("senhaInput").value = "";
}

// 🔹 CONFIRMAR (PEGA SENHA E CHAMA SAQUE)
async function confirmarAcao() {
  const senha = document.getElementById("senhaInput").value;

  if (!senha) return;

  fecharModal();

  if (acaoAtual === "efetuandoSaque") {
    await efetuandoSaque(senha); // 👈 PASSA SENHA
  }
}

// 🔹 SAQUE (MESMA FUNÇÃO, SÓ ADICIONADO SENHA)
async function efetuandoSaque(senha = "") {

  const linha = document.querySelector("#tabela-favorecido tr");
  const colunas = linha.querySelectorAll("td");

  const identificacao = colunas[0].innerText.trim();
  const valor = parseFloat(colunas[1].innerText.replace(",", ".")) || 0;
  const descricao = colunas[2].innerText.trim();
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
    senha // 👈 AQUI FOI A ÚNICA COISA ADICIONADA
  };

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
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `;
  document.head.appendChild(style);

  try {
    await fetch("/saques_projeto", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    setTimeout(() => location.reload(), 2000);

  } catch (err) {
    setTimeout(() => location.reload(), 2000);
  }
}

// async function efetuandoSaque() {
//   const linha = document.querySelector("#tabela-favorecido tr");
//   const colunas = linha.querySelectorAll("td");

//   const payload = {
//     identificacao: colunas[0].innerText.trim(),
//     valor_unidade: parseFloat(colunas[1].innerText.replace(",", ".")) || 0,
//     descricao: colunas[2].innerText.trim(),
//     nome_favorecido: colunas[3].innerText.trim(),
//     cpf_favorecido: colunas[4].innerText.trim(),
//     email_favorecido: colunas[5].innerText.trim(),
//     status: colunas[6].innerText.trim()
//   };

//   // Overlay carregando
//   const overlay = document.createElement("div");
//   overlay.id = "overlay-processando";
//   overlay.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:9999;";
//   overlay.innerHTML = `
//     <div style="color:#fff;font-size:22px;font-family:monospace;">
//       Processando saque... Aguarde...
//       <br><br>
//       <div class="loader"></div>
//     </div>`;
//   document.body.appendChild(overlay);

//   const style = document.createElement("style");
//   style.innerHTML = `
//     .loader {
//       border: 6px solid #f3f3f3;
//       border-top: 6px solid #3498db;
//       border-radius: 50%;
//       width: 40px;
//       height: 40px;
//       animation: spin 1s linear infinite;
//       margin:auto;
//     }
//     @keyframes spin {0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}
//   `;
//   document.head.appendChild(style);

//   try {
//     await fetch("/saques_projeto", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify(payload)
//     });
//     setTimeout(() => location.reload(), 2000);
//   } catch (err) {
//     setTimeout(() => location.reload(), 2000);
//   }
// }