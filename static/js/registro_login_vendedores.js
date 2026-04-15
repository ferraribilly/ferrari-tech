




document.getElementById("formRegistro").addEventListener("submit", async function(e) {
    e.preventDefault();

    const formData = {
        nome: this.nome.value,
        sobrenome: this.sobrenome.value,
        cpf: this.cpf.value,
        dt_nascimento: this.dt_nascimento.value,
        email: this.email.value,
        chave_pix: this.chave_pix.value
    };

    console.log("ENVIANDO:", formData);

    const res = await fetch("/registrar/vendedores", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
    });

    const data = await res.json();
    console.log("RESPOSTA:", data);

    if (data.status === "sucesso") {
        window.location.href = `/fechamento`;
    }
});




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
        window.location.href = `/fechamento`;
    } else {
        document.getElementById("loginMsg").innerHTML =
            `<div class="alert alert-danger">${data.mensagem}</div>`;
    }
});



  