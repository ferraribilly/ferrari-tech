document.addEventListener("DOMContentLoaded", function () {

    const btn = document.querySelector("#tableRegistro button");
    const loading = document.getElementById("loadingOverlay");

    if (!btn) {
        console.error("BOTÃO NÃO ENCONTRADO");
        return;
    }

    btn.addEventListener("click", async function (e) {
        e.preventDefault();

        const linha = document.querySelector("#tableRegistro tbody tr");

        const nome = linha.querySelector("#nome")?.innerText.trim();
        const sobrenome = linha.querySelector("#sobrenome")?.innerText.trim();
        const dt_nascimento = linha.querySelector("#dt_nascimento")?.value;
        const cpf = linha.querySelector("#cpf")?.innerText.trim();
        const email = linha.querySelector("#email")?.innerText.trim();
        const estado = linha.querySelector("#estado")?.value;
        const chave_pix = linha.querySelector("#chave_pix")?.innerText.trim();
        const vendedor = linha.querySelector("#vendedor")?.innerText.trim();

        const formData = {
            nome,
            sobrenome,
            dt_nascimento,
            cpf,
            email,
            estado,
            chave_pix,
            vendedor: vendedor || "ADMIN"
        };

        if (!nome || !sobrenome || !dt_nascimento || !cpf || !email || !estado || !chave_pix) {
            alert("Preencha todos os campos");
            return;
        }

        try {
            // 🔥 MOSTRA ANIMAÇÃO
            loading.style.display = "flex";

            const res = await fetch("/registrar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });

            const data = await res.json();

            if (data.status === "sucesso") {

                // 🔥 RECARREGA A PÁGINA DIRETO
                window.location.reload();

            } else {
                loading.style.display = "none";
                alert(data.mensagem || "Erro ao cadastrar");
            }

        } catch (err) {
            loading.style.display = "none";
            console.error("ERRO FETCH:", err);
            alert("Erro na requisição");
        }
    });

});