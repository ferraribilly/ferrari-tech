
// LOGIN (USUARIOS)
document.getElementById("formLogin").addEventListener("submit", async function(e) {
    e.preventDefault();

    const cpf = document.getElementById("cpfLogin").value.trim();

    const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cpf: cpf })
    });

    const data = await res.json();

    if (data.status === "sucesso") {
        window.location.href = `/dia_das_maes?id=${data.usuario_id}`;
    } else {
        document.getElementById("loginMsg").innerHTML =
            `<div class="alert alert-danger">${data.mensagem}</div>`;
    }
});



  