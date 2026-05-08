// 🔥 LOADING
function showDelete() {
  document.getElementById("loadingDelete").style.display = "flex";
}

function hideDelete() {
  document.getElementById("loadingDelete").style.display = "none";
}

// 🔥 DELETE
async function deletarProjeto(tipo, btn) {

  if (!confirm("Tem certeza que deseja deletar?")) return;

  const row = btn.closest("tr");
  const id = row.querySelector("[data-id]").textContent.trim();

  console.log("ID ENVIADO:", id);

  showDelete();

  try {
    const res = await fetch("/deletar_projeto/" + id, {
      method: "DELETE"
    });

    let result = {};

    try {
      result = await res.json();
    } catch (e) {
      console.warn("Resposta não é JSON");
    }

    console.log("STATUS:", res.status);
    console.log("RESPOSTA:", result);

    // 🔥 SÓ REMOVE SE DEU CERTO
    if (res.ok && result.status === "sucesso") {

      row.remove();

      setTimeout(() => {
        location.reload();
      }, 800);

    } else {
      hideDelete();
      alert("Erro ao deletar: " + (result.mensagem || "falha desconhecida"));
    }

  } catch (err) {
    console.error("ERRO FETCH:", err);
    hideDelete();
    alert("Erro na requisição");
  }
}