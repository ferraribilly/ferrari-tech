// LOGIN (CORRIGIDO)
document.getElementById("formLogin").addEventListener("submit", async function(e) {
    e.preventDefault();

    const cpf = document.getElementById("cpfLogin").value.trim();

    const res = await fetch("/login/vendedores", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cpf: cpf })
    });

    const data = await res.json();

    if (data.status === "sucesso") {
        window.location.href = `/graficos/resumo/sistema/detalhes`;
    } else {
        document.getElementById("loginMsg").innerHTML =
            `<div class="alert alert-danger">${data.mensagem}</div>`;
    }
});

