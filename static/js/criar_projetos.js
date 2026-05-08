document.getElementById("criar-projeto").addEventListener("submit", async function (e) {

    e.preventDefault();

    const btn = this.querySelector("button[type='submit']");
    const overlay = document.getElementById("loading-overlay");

    btn.disabled = true;
    btn.innerText = "GERANDO...";
    overlay.style.display = "flex";

    const imgFile = document.querySelector("input[name='imagem_projeto']").files[0];
    const videoFile = document.querySelector("input[name='video_instrucao']").files[0];

    const formData = new FormData();

    if (imgFile) formData.append("imagem_projeto", imgFile);
    if (videoFile) formData.append("video_instrucao", videoFile);

    const upload = await fetch("/upload_media", {
        method: "POST",
        body: formData
    });

    const media = await upload.json();

    const data = {

        nome_projeto: this.nome_projeto.value,

        valor_injetado_premiacao: this.valor_injetado_premiacao.value,
        horario_sorteio: this.horario_sorteio.value,

        quantidade: this.quantidade.value,
        valor_unidade: this.valor_unidade.value,
        dt_sorteio: this.dt_sorteio.value,

        imagem_projeto: media.imagem_url || "",
        video_instrucao: media.video_url || "",

        link_instagram: this.link_instagram.value || "",
        link_youtube: this.link_youtube.value || "",
        link_whatsapp_grupo: this.link_whatsapp_grupo.value || "",
        link_whatsapp_canal: this.link_whatsapp_canal.value || "",
        link_whatsapp_suporte: this.link_whatsapp_suporte.value || "",
        link_tiktok: this.link_tiktok.value || "",
        link_facebook: this.link_facebook.value || "",
        link_kwai: this.link_kwai.value || ""
    };

    const res = await fetch("/criar_projeto", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const result = await res.json();

    btn.innerText = "CRIADO ✔";
    overlay.style.display = "none";

    setTimeout(() => {
        window.location.href = "/resumo";
    }, 800);
});