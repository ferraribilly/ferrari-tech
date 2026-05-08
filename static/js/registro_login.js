document.getElementById("formRegistro").addEventListener("submit", async function(e) {
    e.preventDefault();

    const estado = document.getElementById("estado").value;
    const vendedor = document.getElementById("vendedorInput").value;

    const formData = {
        nome: document.getElementById("nome").value.trim(),
        sobrenome: document.getElementById("sobrenome").value.trim(),
        cpf: document.getElementById("cpf").value.trim(),
        dt_nascimento: document.getElementById("dt_nascimento").value,
        email: document.getElementById("email").value.trim(),
        estado: estado,
        vendedor: vendedor || "Plataforma Ferrari Tech",
        chave_pix: document.getElementById("chave_pix").value.trim()
    };

    console.log("ENVIANDO:", formData);

    if (!estado) {
        alert("Selecione o estado");
        return;
    }

    const res = await fetch("/registrar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
    });

    const data = await res.json();
    console.log("RESPOSTA:", data);

    if (data.status === "sucesso") {
        window.location.href = `/vitoria_visionaria/projeto-desenvolvimento-fase-teste/codigo_servico/1722/${data.usuario._id}`;
    } else {
        alert(data.mensagem || "Erro ao cadastrar");
    }
});


// ================= ESTADOS =================
document.addEventListener("DOMContentLoaded", function() {
    const estadoSelect = document.getElementById("estado");

    const estados = [
        { uf: "AC", nome: "Acre" }, { uf: "AL", nome: "Alagoas" }, { uf: "AP", nome: "Amapá" },
        { uf: "AM", nome: "Amazonas" }, { uf: "BA", nome: "Bahia" }, { uf: "CE", nome: "Ceará" },
        { uf: "DF", nome: "Distrito Federal" }, { uf: "ES", nome: "Espírito Santo" },
        { uf: "GO", nome: "Goiás" }, { uf: "MA", nome: "Maranhão" }, { uf: "MT", nome: "Mato Grosso" },
        { uf: "MS", nome: "Mato Grosso do Sul" }, { uf: "MG", nome: "Minas Gerais" },
        { uf: "PA", nome: "Pará" }, { uf: "PB", nome: "Paraíba" }, { uf: "PR", nome: "Paraná" },
        { uf: "PE", nome: "Pernambuco" }, { uf: "PI", nome: "Piauí" }, { uf: "RJ", nome: "Rio de Janeiro" },
        { uf: "RN", nome: "Rio Grande do Norte" }, { uf: "RS", nome: "Rio Grande do Sul" },
        { uf: "RO", nome: "Rondônia" }, { uf: "RR", nome: "Roraima" }, { uf: "SC", nome: "Santa Catarina" },
        { uf: "SP", nome: "São Paulo" }, { uf: "SE", nome: "Sergipe" }, { uf: "TO", nome: "Tocantins" }
    ];

    estados.forEach(estado => {
        const option = document.createElement("option");
        option.value = estado.uf;
        option.textContent = estado.nome;
        estadoSelect.appendChild(option);
    });
});


// ================= VENDEDOR =================
document.addEventListener('DOMContentLoaded', function () {

    const input = document.getElementById('vendedorInput');
    const modalElement = document.getElementById('vendedorModal');
    const modal = new bootstrap.Modal(modalElement);

    document.querySelectorAll('.vendor-option').forEach(option => {
        option.addEventListener('click', function () {
            input.value = this.textContent.trim();
            modal.hide();
        });
    });

});


// ================= SEGURANÇA =================
setTimeout(() => {
  const el = document.querySelector(".security-notice");
  if (el) el.style.display = "none";
}, 5000);

document.addEventListener('DOMContentLoaded', function () {

    const input = document.getElementById('vendedorInput');
    const modalElement = document.getElementById('vendedorModal');
    const modal = new bootstrap.Modal(modalElement);

    document.querySelectorAll('.vendor-option').forEach(option => {
        option.addEventListener('click', function () {
            input.value = this.textContent.trim();
            modal.hide();
        });
    });

});