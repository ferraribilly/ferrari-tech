//function validarCertificado(certificado.txt)

// ================= FUNÇÕES DE VALIDAÇÃO =================

function validarCPF(cpf) {
    cpf = cpf.replace(/\D/g, ''); // Remove pontos e traços

    if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false;
    
    let soma = 0, resto;

    for (let i = 1; i <= 9; i++) {
        soma += parseInt(cpf.substring(i - 1, i)) * (11 - i);
    }

    resto = (soma * 10) % 11;

    if ((resto === 10) || (resto === 11)) resto = 0;

    if (resto !== parseInt(cpf.substring(9, 10))) return false;
    
    soma = 0;

    for (let i = 1; i <= 10; i++) {
        soma += parseInt(cpf.substring(i - 1, i)) * (12 - i);
    }

    resto = (soma * 10) % 11;

    if ((resto === 10) || (resto === 11)) resto = 0;

    if (resto !== parseInt(cpf.substring(10, 11))) return false;
    
    return true;
}

function validarMaioridade(dataNasc) {
    const hoje = new Date();
    const nasc = new Date(dataNasc);

    let idade = hoje.getFullYear() - nasc.getFullYear();
    const m = hoje.getMonth() - nasc.getMonth();

    if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) {
        idade--;
    }

    return idade >= 18;
}

// 📍 FUNÇÃO DE CAPTURA DIRETA (SEM CAIXA VISUAL)
function capturarCoordenadasDireto() {
    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
            (position) => resolve({ latitude: position.coords.latitude, longitude: position.coords.longitude }),
            (error) => reject(error),
            { enableHighAccuracy: true, timeout: 8000 }
        );
    });
}


// ================= EVENTO PRINCIPAL (REGISTRO) =================

document.getElementById("formRegistro").addEventListener("submit", async function(e) {

    e.preventDefault();

    const loader = document.getElementById("loadingOverlay");
    const loaderText = document.getElementById("loadingText");
    
    // Captura de Dados
    const cpf = document.getElementById("cpf").value.trim();
    const dtNasc = document.getElementById("dt_nascimento").value;

    // 1. Iniciar Animação
    loader.style.display = "flex";
    loaderText.innerText = "Verificando dados...";

    // Pequeno delay para a animação ser percebida pelo usuário
    await new Promise(r => setTimeout(r, 800));

    // 2. Validações de Segurança
    if (!validarCPF(cpf)) {
        loader.style.display = "none";
        alert("O CPF digitado é inválido. Por favor, confira os números.");
        return;
    }

    if (!validarMaioridade(dtNasc)) {
        loader.style.display = "none";
        alert("Cadastro permitido apenas para maiores de 18 anos.");
        return;
    }

    // 📍 3. CHECAGEM INTELIGENTE DE PERMISSÃO (Evita o Bug do botão fantasma)
    let coords = null;
    let precisaMostrarCaixa = true;

    if (!navigator.geolocation) {
        loader.style.display = "none";
        alert("Seu navegador não suporta geolocalização.");
        return;
    }

    if (navigator.permissions) {
        try {
            const permissao = await navigator.permissions.query({ name: 'geolocation' });
            // Se já foi aceito anteriormente pelo usuário no navegador dele
            if (permissao.state === 'granted') {
                loaderText.innerText = "Coletando segurança geográfica...";
                coords = await capturarCoordenadasDireto();
                precisaMostrarCaixa = false; // Ignora a criação da caixinha com botão
            } else if (permissao.state === 'denied') {
                loader.style.display = "none";
                alert("❌ Acesso à localização bloqueado no navegador. Ative nas configurações do site para prosseguir.");
                return;
            }
        } catch (err) {
            console.warn("Erro ao checar permissões prévias, usando fallback manual.", err);
        }
    }

    // Se NÃO tiver permissão prévia concedida, renderiza a caixa com botão na tela
    if (precisaMostrarCaixa) {
        loader.style.display = "none";

        coords = await new Promise((resolve) => {
            const caixaAviso = document.createElement("div");
            caixaAviso.style.position = "fixed";
            caixaAviso.style.top = "50%";
            caixaAviso.style.left = "50%";
            caixaAviso.style.transform = "translate(-50%, -50%)";
            caixaAviso.style.backgroundColor = "#fff";
            caixaAviso.style.padding = "25px";
            caixaAviso.style.boxShadow = "0 0 15px rgba(0,0,0,0.5)";
            caixaAviso.style.zIndex = "99999";
            caixaAviso.style.borderRadius = "8px";
            caixaAviso.style.textAlign = "center";
            caixaAviso.style.fontFamily = "sans-serif";
            caixaAviso.style.border = "2px solid #00BFFF";

            caixaAviso.innerHTML = `
                <h4 style="margin-top:0; color:#333;">🔒 Segurança Sala Contábil</h4>
                <p style="color:#555; font-size:14px; margin-bottom:20px;">
                    Para concluir o seu registro, é obrigatório permitir o envio da sua localização.
                </p>
                <button id="btnAutorizarGeo" style="
                    background-color: #00BFFF; 
                    color: white; 
                    border: none; 
                    padding: 10px 20px; 
                    font-size: 14px; 
                    font-weight: bold; 
                    border-radius: 5px; 
                    cursor: pointer;">
                    Autorizar e Enviar Cadastro
                </button>
            `;

            const fundoEscuro = document.createElement("div");
            fundoEscuro.style.position = "fixed";
            fundoEscuro.style.top = "0";
            fundoEscuro.style.left = "0";
            fundoEscuro.style.width = "100vw";
            fundoEscuro.style.height = "100vh";
            fundoEscuro.style.backgroundColor = "rgba(0,0,0,0.6)";
            fundoEscuro.style.zIndex = "99998";

            document.body.appendChild(fundoEscuro);
            document.body.appendChild(caixaAviso);

            document.getElementById("btnAutorizarGeo").addEventListener("click", function() {
                this.innerText = "Capturando...";
                this.disabled = true;

                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        fundoEscuro.remove();
                        caixaAviso.remove();
                        resolve({
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        });
                    },
                    (error) => {
                        fundoEscuro.remove();
                        caixaAviso.remove();
                        alert("❌ Cadastro cancelado: Você precisa autorizar o acesso à localização para operar na sala contábil.<br> Caso ja tenha aparecido mensagem mesmo dado permissão e so clicar novamente no botão registrar que normal a mensagem devido sala segura!");
                        resolve(null);
                    },
                    { enableHighAccuracy: true, timeout: 12000 }
                );
            });
        });
    }

    // Se o usuário recusou ou a captura falhou na caixinha, encerra aqui
    if (!coords || !coords.latitude || !coords.longitude) {
        return;
    }

    // Retoma o fluxo visual do loader original para persistência de dados
    loader.style.display = "flex";
    loaderText.innerText = "Finalizando seu cadastro...";

    const formData = {
        nome: document.getElementById("nome").value.trim(),
        sobrenome: document.getElementById("sobrenome").value.trim(),
        cpf: cpf,
        dt_nascimento: dtNasc,
        email: document.getElementById("email").value.trim(),
        chave_pix: document.getElementById("chave_pix").value.trim(),
        comissao: document.getElementById("comissao").value,
        latitude: coords.latitude,
        longitude: coords.longitude
    };

    try {
        const res = await fetch("/registrar/vendedores", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
        });

        const data = await res.json();

        if (data.status === "sucesso") {
            loaderText.innerText = "Tudo pronto! Entrando...";
            setTimeout(() => {
                window.location.href = `/admin/${data.vendedor._id}`;
            }, 1000);
        } else {
            loader.style.display = "none";
            alert(data.mensagem || "Ocorreu um erro ao processar o registro.");
        }

    } catch (error) {
        console.error(error);
        loader.style.display = "none";
        alert("Erro de conexão. Verifique sua internet.");
    }
});


document.addEventListener("DOMContentLoaded", function() {
    setTimeout(() => {
        const el = document.querySelector(".security-notice");
        if (el) el.style.opacity = "0"; 
        setTimeout(() => {
            if (el) el.style.display = "none";
        }, 500);
    }, 5000);
});






// //function validarCertificado(certificado.txt)

// // ================= FUNÇÕES DE VALIDAÇÃO =================

// function validarCPF(cpf) {

//     cpf = cpf.replace(/\D/g, ''); // Remove pontos e traços

//     if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false;
    
//     let soma = 0, resto;

//     for (let i = 1; i <= 9; i++) {
//         soma += parseInt(cpf.substring(i - 1, i)) * (11 - i);
//     }

//     resto = (soma * 10) % 11;

//     if ((resto === 10) || (resto === 11)) resto = 0;

//     if (resto !== parseInt(cpf.substring(9, 10))) return false;
    
//     soma = 0;

//     for (let i = 1; i <= 10; i++) {
//         soma += parseInt(cpf.substring(i - 1, i)) * (12 - i);
//     }

//     resto = (soma * 10) % 11;

//     if ((resto === 10) || (resto === 11)) resto = 0;

//     if (resto !== parseInt(cpf.substring(10, 11))) return false;
    
//     return true;
// }

// function validarMaioridade(dataNasc) {

//     const hoje = new Date();
//     const nasc = new Date(dataNasc);

//     let idade = hoje.getFullYear() - nasc.getFullYear();

//     const m = hoje.getMonth() - nasc.getMonth();

//     if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) {
//         idade--;
//     }

//     return idade >= 18;
// }


// // ================= EVENTO PRINCIPAL (REGISTRO) =================

// document.getElementById("formRegistro").addEventListener("submit", async function(e) {

//     e.preventDefault();

//     const loader = document.getElementById("loadingOverlay");
//     const loaderText = document.getElementById("loadingText");
    
//     // Captura de Dados
//     const cpf = document.getElementById("cpf").value.trim();
//     const dtNasc = document.getElementById("dt_nascimento").value;

//     // 1. Iniciar Animação
//     loader.style.display = "flex";
//     loaderText.innerText = "Verificando dados...";

//     // Pequeno delay para a animação ser percebida pelo usuário
//     await new Promise(r => setTimeout(r, 800));

//     // 2. Validações de Segurança
//     if (!validarCPF(cpf)) {

//         loader.style.display = "none";

//         alert("O CPF digitado é inválido. Por favor, confira os números.");

//         return;
//     }

//     if (!validarMaioridade(dtNasc)) {

//         loader.style.display = "none";

//         alert("Cadastro permitido apenas para maiores de 18 anos.");

//         return;
//     }

//     // 3. Finalização
//     loaderText.innerText = "Finalizando seu cadastro...";

//     const formData = {

//         nome: document.getElementById("nome").value.trim(),

//         sobrenome: document.getElementById("sobrenome").value.trim(),

//         cpf: cpf,

//         dt_nascimento: dtNasc,

//         email: document.getElementById("email").value.trim(),

//         chave_pix: document.getElementById("chave_pix").value.trim(),

//         comissao: document.getElementById("comissao").value
//     };

//     try {

//         const res = await fetch("/registrar/vendedores", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json"
//             },
//             body: JSON.stringify(formData)
//         });

//         const data = await res.json();

//         if (data.status === "sucesso") {

//             loaderText.innerText = "Tudo pronto! Entrando...";

//             setTimeout(() => {

//                 window.location.href = `/admin/${data.vendedor._id}`;

//             }, 1000);

//         } else {

//             loader.style.display = "none";

//             alert(data.mensagem || "Ocorreu um erro ao processar o registro.");
//         }

//     } catch (error) {

//         console.error(error);

//         loader.style.display = "none";

//         alert("Erro de conexão. Verifique sua internet.");
//     }

// });



// document.addEventListener("DOMContentLoaded", function() {

//     // Esconder aviso de segurança após 5 segundos
//     setTimeout(() => {

//         const el = document.querySelector(".security-notice");

//         if (el) el.style.opacity = "0"; // Suave

//         setTimeout(() => {

//             if (el) el.style.display = "none";

//         }, 500);

//     }, 5000);

// });