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
    const senha = document.getElementById("senhaInput").value;
    if (!linhaAtual) return;

    const id = linhaAtual.querySelector("td[data-id]")?.dataset.id;
    if (!senha || !id) return;

    if (acaoAtual === "deletar") {
      const res = await fetch("/deletar-usuario", {
        method: "DELETE",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ id, senha })
      });
      const data = await res.json();
      if (data.sucesso) {
        linhaAtual.remove();
        alert("Usuário deletado com sucesso!");
      } else {
        alert(data.erro);
      }
    }

    if (acaoAtual === "salvar") {
      const estado = linhaAtual.querySelector('[data-field="estado"]')?.innerText.trim();
      const email = linhaAtual.querySelector('[data-field="email"]')?.innerText.trim();
      const chave_pix = linhaAtual.querySelector('[data-field="chave_pix"]')?.innerText.trim();

      const res = await fetch("/editar-usuario", {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ id, senha, estado, email, chave_pix })
      });
      const data = await res.json();
      if (data.sucesso) {
        alert("Usuário atualizado com sucesso!");
      } else {
        alert(data.erro);
      }
    }

    fecharModal();
  }

  window.abrirModal = abrirModal;
  window.fecharModal = fecharModal;
  window.confirmarAcao = confirmarAcao;


