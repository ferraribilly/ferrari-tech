let acaoAtual = null;
let linhaAtual = null;

function abrirModal(acao, btn) {
  acaoAtual = acao;
  linhaAtual = btn.closest("tr");

  document.getElementById("modalSenha").style.display = "flex";
}

function fecharModal() {
  document.getElementById("modalSenha").style.display = "none";
  document.getElementById("senhaInput").value = "";
}

async function confirmarAcao() {
  const senha = document.getElementById("senhaInput").value.trim();

  if (!senha || !linhaAtual) return;

  const id = linhaAtual.querySelector("td[data-id]")?.dataset.id;
  if (!id) return;

  // ===== DELETAR =====
  if (acaoAtual === "deletar") {
    try {
      const res = await fetch("/deletar-vendedor", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, senha })
      });

      const data = await res.json();

      if (data.sucesso) {
        linhaAtual.remove();
        alert("Vendedor deletado com sucesso!");
      } else {
        alert(data.erro || "Erro ao deletar");
      }

    } catch (err) {
      console.error(err);
      alert("Erro na requisição");
    }
  }

  // ===== EDITAR =====
  if (acaoAtual === "salvar") {
    const email = linhaAtual.querySelector('[data-field="email"]')?.innerText.trim();
    const chave_pix = linhaAtual.querySelector('[data-field="chave_pix"]')?.innerText.trim();
    const comissao = linhaAtual.querySelector('[data-field="comissao"]')?.innerText.trim();

    try {
      const res = await fetch("/editar-vendedor", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id,
          senha,
          email,
          chave_pix,
          comissao
        })
      });

      const data = await res.json();

      if (data.sucesso) {
        alert("Vendedor atualizado com sucesso!");
      } else {
        alert(data.erro || "Erro ao editar");
      }

    } catch (err) {
      console.error(err);
      alert("Erro na requisição");
    }
  }

  fecharModal();
}

// GLOBAL
window.abrirModal = abrirModal;
window.fecharModal = fecharModal;
window.confirmarAcao = confirmarAcao;