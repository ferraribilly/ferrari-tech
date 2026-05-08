document.querySelectorAll(".btn-whatsapp").forEach(btn => {
    btn.addEventListener("click", function () {

        let imagens = this.getAttribute("data-imagens");

        try {
            imagens = JSON.parse(imagens);
        } catch (e) {
            console.log("Erro ao converter:", imagens);
            alert("Erro nas imagens");
            return;
        }

        if (!imagens || imagens.length === 0) {
            alert("Sem imagens");
            return;
        }

        let mensagem = "Meus bilhetes 🎫:\n\n";

        imagens.forEach(url => {
            mensagem += url + "\n";
        });

        let link = "https://wa.me/?text=" + encodeURIComponent(mensagem);

        window.open(link, "_blank");
    });
});


