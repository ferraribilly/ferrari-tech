// ================= FUNÇÕES DE VALIDAÇÃO =================

function validarCPF(cpf) {
    cpf = cpf.replace(/\D/g, ''); // Remove pontos e traços
    if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false;
    
    let soma = 0, resto;
    for (let i = 1; i <= 9; i++) soma += parseInt(cpf.substring(i-1, i)) * (11 - i);
    resto = (soma * 10) % 11;
    if ((resto === 10) || (resto === 11)) resto = 0;
    if (resto !== parseInt(cpf.substring(9, 10))) return false;
    
    soma = 0;
    for (let i = 1; i <= 10; i++) soma += parseInt(cpf.substring(i-1, i)) * (12 - i);
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

// ================= FUNÇÕES DE VALIDAÇÃO =================

function validarCPF(cpf) {

    cpf = cpf.replace(/\D/g, ''); // Remove pontos e traços

    if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false;
    
    let soma = 0, resto;

    for (let i = 1; i <= 9; i++) soma += parseInt(cpf.substring(i-1, i)) * (11 - i);

    resto = (soma * 10) % 11;

    if ((resto === 10) || (resto === 11)) resto = 0;

    if (resto !== parseInt(cpf.substring(9, 10))) return false;
    
    soma = 0;

    for (let i = 1; i <= 10; i++) soma += parseInt(cpf.substring(i-1, i)) * (12 - i);

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


// ================= EVENTO PRINCIPAL (REGISTRO) =================

document.getElementById("formRegistro").addEventListener("submit", async function(e) {

    e.preventDefault();

    const loader = document.getElementById("loadingOverlay");

    const loaderText = document.getElementById("loadingText");
    
    // Captura de Dados

    const cpf = document.getElementById("cpf").value.trim();

    const dtNasc = document.getElementById("dt_nascimento").value;

    // const estado = document.getElementById("estado").value;

    const vendedor = document.getElementById("vendedorInput").value;
    const vendedor_id = document.getElementById("vendedorInput").value;

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

    // if (!estado) {

    //     loader.style.display = "none";

    //     alert("Por favor, selecione seu estado.");

    //     return;

    // }

    // 3. Preparar Envio

    loaderText.innerText = "Finalizando seu cadastro...";

    const formData = {

        nome: document.getElementById("nome").value.trim(),

        sobrenome: document.getElementById("sobrenome").value.trim(),

        cpf: cpf,

        dt_nascimento: dtNasc,

        email: document.getElementById("email").value.trim(),

        // estado: estado,

        vendedor: vendedor || "Plataforma Ferrari Tech",
        vendedor_id: vendedor_id || "",

        chave_pix: document.getElementById("chave_pix").value.trim()

    };

    try {

        const res = await fetch("/registrar", {

            method: "POST",

            headers: { "Content-Type": "application/json" },

            body: JSON.stringify(formData)

        });

        const data = await res.json();

        if (data.status === "sucesso") {

            loaderText.innerText = "Tudo pronto! Entrando...";

            setTimeout(() => {

                window.location.href = `/raspadinha/${data.usuario._id}`;

            }, 1000);

        } else {

            loader.style.display = "none";

            alert(data.mensagem || "Ocorreu um erro ao processar o registro.");

        }

    } catch (error) {

        loader.style.display = "none";

        alert("Erro de conexão. Verifique sua internet.");

    }

});


// ================= PREENCHIMENTO DE ESTADOS =================

// document.addEventListener("DOMContentLoaded", function() {

//     const estadoSelect = document.getElementById("estado");

//     const estados = [

//         { uf: "AC", nome: "Acre" }, { uf: "AL", nome: "Alagoas" }, { uf: "AP", nome: "Amapá" },

//         { uf: "AM", nome: "Amazonas" }, { uf: "BA", nome: "Bahia" }, { uf: "CE", nome: "Ceará" },

//         { uf: "DF", nome: "Distrito Federal" }, { uf: "ES", nome: "Espírito Santo" },

//         { uf: "GO", nome: "Goiás" }, { uf: "MA", nome: "Maranhão" }, { uf: "MT", nome: "Mato Grosso" },

//         { uf: "MS", nome: "Mato Grosso do Sul" }, { uf: "MG", nome: "Minas Gerais" },

//         { uf: "PA", nome: "Pará" }, { uf: "PB", nome: "Paraíba" }, { uf: "PR", nome: "Paraná" },

//         { uf: "PE", nome: "Pernambuco" }, { uf: "PI", nome: "Piauí" }, { uf: "RJ", nome: "Rio de Janeiro" },

//         { uf: "RN", nome: "Rio Grande do Norte" }, { uf: "RS", nome: "Rio Grande do Sul" },

//         { uf: "RO", nome: "Rondônia" }, { uf: "RR", nome: "Roraima" }, { uf: "SC", nome: "Santa Catarina" },

//         { uf: "SP", nome: "São Paulo" }, { uf: "SE", nome: "Sergipe" }, { uf: "TO", nome: "Tocantins" }

//     ];

//     estados.forEach(estado => {

//         const option = document.createElement("option");

//         option.value = estado.uf;

//         option.textContent = estado.nome;

//         estadoSelect.appendChild(option);

//     });

document.addEventListener("DOMContentLoaded", function() {

    // Lógica do Modal de Vendedor

    const inputVendedor = document.getElementById('vendedorInput');

    const modalElement = document.getElementById('vendedorModal');
    
    // Verifica se o modal existe antes de instanciar (evita erros se o HTML mudar)

    if (modalElement) {

        const modal = new bootstrap.Modal(modalElement);

        document.querySelectorAll('.vendor-option').forEach(option => {

            option.addEventListener('click', function () {

                inputVendedor.value = this.textContent.trim();

                modal.hide();

            });

        });

    }

    // Esconder aviso de segurança após 5 segundos

    setTimeout(() => {

        const el = document.querySelector(".security-notice");

        if (el) el.style.opacity = "0"; // Suave

        setTimeout(() => { if(el) el.style.display = "none" }, 500);

    }, 5000);

});