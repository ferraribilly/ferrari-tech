document.addEventListener("DOMContentLoaded", () => {

    const btn = document.getElementById("btn-pagar");

    const loading = document.getElementById("loading-pagamento");

    if (!btn || !loading) return;

    btn.addEventListener("click", (e) => {

        e.preventDefault();

        // MOSTRA SPINNER
        loading.style.display = "flex";

        // força renderização na tela
        requestAnimationFrame(() => {

            const nome = document.getElementById("nome")?.innerText || "";

            const sobrenome = document.getElementById("sobrenome")?.innerText || "";

            const cpf = document.getElementById("cpf")?.innerText || "";

            const email = document.getElementById("email")?.innerText || "";

            const vendedor = document.getElementById("vendedor")?.innerText || "";

            const quantidade = parseInt(
                document.querySelector(".buy-slide .quantidade")?.innerText || "1"
            );

            setTimeout(() => {

                window.location.href =
                    `/payment_qrcode_pix/pagamento_pix/ferrari-tech/{{ usuario_id }}`
                    + `?nome=${encodeURIComponent(nome)}`
                    + `&sobrenome=${encodeURIComponent(sobrenome)}`
                    + `&vendedor=${encodeURIComponent(vendedor)}`
                    + `&cpf=${encodeURIComponent(cpf)}`
                    + `&email=${encodeURIComponent(email)}`
                    + `&quantidade=${quantidade}`;

            }, 500);

        });

    });

});