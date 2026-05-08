let projetoAtual = null;
let imagemEdit = null;
let videoEdit = null;

// 🖼️ IMAGEM
function abrirModalImagem(id, url) {
    projetoAtual = id;
    imagemEdit = null;

    document.getElementById("modalImg").style.display = "flex";
    document.getElementById("imgExpandida").src = url;
}

function trocarImagem(event) {
    const file = event.target.files[0];
    if (!file) return;

    imagemEdit = file;

    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById("imgExpandida").src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function salvarImagemEditada() {
    if (!imagemEdit || !projetoAtual) return;

    const formData = new FormData();
    formData.append("imagem_projeto", imagemEdit);

    fetch(`/atualizar_imagem/${projetoAtual}`, {
        method: "POST",
        body: formData
    })
    .then(r => r.json())
    .then(res => {
        if (res.status === "imagem atualizada") {
            location.reload();
        }
    })
    .catch(err => console.log(err));

    document.getElementById("modalImg").style.display = "none";
}

// 🎥 VÍDEO
function abrirModalVideo(id) {
    projetoAtual = id;
    videoEdit = null;

    document.getElementById("modalVideo").style.display = "flex";
}

function salvarVideoEditado() {
    const file = document.getElementById("fileVideoEdit").files[0];
    if (!file || !projetoAtual) return;

    const formData = new FormData();
    formData.append("video_instrucao", file);

    fetch(`/atualizar_video/${projetoAtual}`, {
        method: "POST",
        body: formData
    })
    .then(r => r.json())
    .then(res => {
        if (res.status === "video atualizado") {
            location.reload();
        }
    })
    .catch(err => console.log(err));

    document.getElementById("modalVideo").style.display = "none";
}

// 💾 DADOS
function atualizarTodosDados(btn) {

    const tr = btn.closest("tr");
    if (!tr) return;

    const id = tr.querySelector("[data-id]").getAttribute("data-id");
    if (!id) return;

    const data = {
        nome_projeto: tr.children[1].innerText.trim(),
        valor_injetado_premiacao: tr.children[2].innerText.trim(),
        quantidade: tr.children[3].innerText.trim(),
        valor_unidade: tr.children[4].innerText.trim(),
        dt_sorteio: tr.children[5].innerText.trim(),
        horario_sorteio: tr.children[6].innerText.trim(),

        link_instagram: tr.children[7].innerText.trim(),
        link_whatsapp_suporte: tr.children[8].innerText.trim(),
        link_whatsapp_grupo: tr.children[9].innerText.trim(),
        link_whatsapp_canal: tr.children[10].innerText.trim(),
        link_youtube: tr.children[11].innerText.trim(),
        link_facebook: tr.children[12].innerText.trim(),
        link_tiktok: tr.children[13].innerText.trim(),
        link_kwai: tr.children[14].innerText.trim()
    };

    fetch(`/atualizar_dados/${id}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(res => {
        if (res.status === "dados atualizados") {
            location.reload();
        }
    })
    .catch(err => console.log(err));
}