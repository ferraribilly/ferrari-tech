

function fecharPopup() {
    document.getElementById("adPopup").style.display = "none";
  }


document.getElementById("formRegistro").addEventListener("submit", async function(e) {
    e.preventDefault();

    const formData = {
        nome: this.nome.value,
        sobrenome: this.sobrenome.value,
        cpf: this.cpf.value,
        dt_nascimento: this.dt_nascimento.value,
        email: this.email.value,
        vendedor: document.getElementById("vendedorInput").value,
        chave_pix: this.chave_pix.value
    };

    console.log("ENVIANDO:", formData);

    const res = await fetch("/registrar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
    });

    const data = await res.json();
    console.log("RESPOSTA:", data);

    if (data.status === "sucesso") {
        window.location.href = `/dia_das_maes?id=${data.usuario._id}`;
    }
});



  