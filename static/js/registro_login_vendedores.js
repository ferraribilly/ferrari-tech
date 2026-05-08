document.getElementById("formRegistro").addEventListener("submit", async function(e) {
    e.preventDefault();

    const formData = {
        nome: this.nome.value,
        sobrenome: this.sobrenome.value,
        cpf: this.cpf.value,
        dt_nascimento: this.dt_nascimento.value,
        email: this.email.value,
        chave_pix: this.chave_pix.value,
        comissao: this.comissao.value

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
        window.location.href = `/graficos/resumo/sistema/detalhes`;
    }
});





  