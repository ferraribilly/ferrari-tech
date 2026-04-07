 function fecharPopup() {
    document.getElementById("adPopup").style.display = "none";
  }


// REGISTRO
document.getElementById("formRegistro").addEventListener("submit", async function(e) {
    e.preventDefault();

    const formData = Object.fromEntries(new FormData(this).entries());

    const res = await fetch("/registrar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
    });

    const data = await res.json();

    if (data.status === "sucesso") {
        document.getElementById("registroMsg").innerHTML =
            `<div class="alert alert-success">Cadastro realizado!</div>`;

        setTimeout(() => {
            window.location.href = `/dia_das_maes?id=${data.usuario._id}`;
        }, 800);

    } else {
        document.getElementById("registroMsg").innerHTML =
            `<div class="alert alert-danger">${data.mensagem}</div>`;
    }
});


// LOGIN (CORRIGIDO)
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

  