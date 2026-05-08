  let links = {};

// 🔥 PREVIEW IMAGEM
function previewImage(event) {
  const file = event.target.files[0];
  const img = document.getElementById("preview_img");

  if (file) {
    img.src = URL.createObjectURL(file);
    img.style.display = "block";
  }
}

// 🔥 PREVIEW VIDEO
function previewVideo(event) {
  const file = event.target.files[0];
  const video = document.getElementById("preview_video");

  if (file) {
    video.src = URL.createObjectURL(file);
    video.style.display = "block";
  }
}

// 🔥 LINKS
function abrirCardLink() {
  document.getElementById("card_link").style.display = "block";
}

function confirmarLink() {
  const tipo = document.getElementById("select_rede").value;
  const url = document.getElementById("input_link").value;

  if (!tipo || !url) return;

  links[tipo] = url;

  const lista = document.getElementById("lista_links");
  lista.innerHTML += `<div>${tipo}: ${url}</div>`;

  document.getElementById("input_link").value = "";
  document.getElementById("card_link").style.display = "none";
}

// 🔥 CONTROLE LOADING
function mostrarLoading() {
  document.getElementById("loadingOverlay").style.display = "flex";
}

function esconderLoading() {
  document.getElementById("loadingOverlay").style.display = "none";
}

// 🔥 ENVIAR PARA BACKEND
async function salvarProjeto() {

  mostrarLoading();

  const data = {
    nome_projeto: document.getElementById("nome_projeto").innerText,
    valor_injetado_premiacao: document.getElementById("valor_injetado_premiacao").innerText,
    quantidade: document.getElementById("quantidade").innerText,
    valor_unidade: document.getElementById("valor").innerText,
    dt_sorteio: document.getElementById("dt_sorteio").value,
    horario_sorteio: document.getElementById("hora_sorteio").innerText,

    imagem_projeto: document.getElementById("preview_img").src,
    video_instrucao: document.getElementById("preview_video").src,

    link_instagram: links.instagram || "",
    link_youtube: links.youtube || "",
    link_whatsapp_grupo: links.whatsapp_grupo || "",
    link_whatsapp_canal: links.whatsapp_canal || "",
    link_whatsapp_suporte: links.whatsapp_suporte || "",
    link_tiktok: links.tiktok || "",
    link_facebook: links.facebook || "",
    link_kwai: links.kwai || "",

    status: "ativo"
  };

  try {
    const res = await fetch("/criar_projeto", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const result = await res.json();
    console.log(result);

    // 🔥 SUCESSO → RECARREGA
    setTimeout(() => {
      location.reload();
    }, 1200);

  } catch (err) {
    console.error(err);
    esconderLoading();
    alert("Erro ao criar projeto");
  }
}

































// let links = {};

// // 🔥 PREVIEW IMAGEM
// function previewImage(event) {
//   const file = event.target.files[0];
//   const img = document.getElementById("preview_img");

//   if (file) {
//     img.src = URL.createObjectURL(file);
//     img.style.display = "block";
//   }
// }

// // 🔥 PREVIEW VIDEO
// function previewVideo(event) {
//   const file = event.target.files[0];
//   const video = document.getElementById("preview_video");

//   if (file) {
//     video.src = URL.createObjectURL(file);
//     video.style.display = "block";
//   }
// }

// // 🔥 LINKS
// function abrirCardLink() {
//   document.getElementById("card_link").style.display = "block";
// }

// function confirmarLink() {
//   const tipo = document.getElementById("select_rede").value;
//   const url = document.getElementById("input_link").value;

//   if (!tipo || !url) return;

//   links[tipo] = url;

//   const lista = document.getElementById("lista_links");
//   lista.innerHTML += `<div>${tipo}: ${url}</div>`;

//   document.getElementById("input_link").value = "";
//   document.getElementById("card_link").style.display = "none";
// }

// // 🔥 CONTROLE LOADING
// function mostrarLoading() {
//   document.getElementById("loadingOverlay").style.display = "flex";
// }

// function esconderLoading() {
//   document.getElementById("loadingOverlay").style.display = "none";
// }

// // 🔥 ENVIAR PARA BACKEND
// async function salvarProjeto() {

//   mostrarLoading();

//   const data = {
//     nome_projeto: document.getElementById("nome_projeto").innerText,
//     valor_injetado_premiacao: document.getElementById("valor_injetado_premiacao").innerText,
//     quantidade: document.getElementById("quantidade").innerText,
//     valor_unidade: document.getElementById("valor").innerText,
//     dt_sorteio: document.getElementById("dt_sorteio").value,
//     horario_sorteio: document.getElementById("hora_sorteio").innerText,

//     imagem_projeto: document.getElementById("preview_img").src,
//     video_instrucao: document.getElementById("preview_video").src,

//     link_instagram: links.instagram || "",
//     link_youtube: links.youtube || "",
//     link_whatsapp_grupo: links.whatsapp_grupo || "",
//     link_whatsapp_canal: links.whatsapp_canal || "",
//     link_whatsapp_suporte: links.whatsapp_suporte || "",
//     link_tiktok: links.tiktok || "",
//     link_facebook: links.facebook || "",
//     link_kwai: links.kwai || "",

//     status: "ativo"
//   };

//   try {
//     const res = await fetch("/criar_projeto", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json"
//       },
//       body: JSON.stringify(data)
//     });

//     const result = await res.json();
//     console.log(result);

//     // 🔥 SUCESSO → RECARREGA
//     setTimeout(() => {
//       location.reload();
//     }, 1200);

//   } catch (err) {
//     console.error(err);
//     esconderLoading();
//     alert("Erro ao criar projeto");
//   }
// }