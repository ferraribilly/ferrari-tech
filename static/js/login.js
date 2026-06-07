
// LOGIN (USUARIOS)
document.getElementById("formLogin").addEventListener("submit", async function(e) {
    e.preventDefault();

    const email = document.getElementById("emailLogin").value.trim();

    try {
        const res = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email })
        });

        const data = await res.json();

        if (data.status === "sucesso") {
            // Redireciona corretamente com o usuario_id na rota
            window.location.href = `/raspadinha/${data.usuario_id}`;
        } else {
            document.getElementById("loginMsg").innerHTML =
                `<div class="alert alert-danger">${data.mensagem}</div>`;
        }
    } catch (error) {
        document.getElementById("loginMsg").innerHTML =
            `<div class="alert alert-danger">Erro de conexão</div>`;
    }
});