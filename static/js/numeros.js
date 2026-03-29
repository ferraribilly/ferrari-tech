const grid = document.getElementById("grid");
// const modal = document.getElementById("modal");
const numeroEscolhido = document.getElementById("numeroEscolhido");

// gerar 000 até 999 números
for (let i = 0; i <= 999; i++) {
    const div = document.createElement("div");
    div.className = "item";

    const numeroFormatado = i.toString().padStart(3, '0'); // AQUI

    div.textContent = numeroFormatado;

    div.onclick = () => {
        numeroEscolhido.textContent = numeroFormatado; // AQUI também
        modal.style.display = "flex";
    };

    grid.appendChild(div);
}

function fechar() {
    modal.style.display = "none";
    document.getElementById("qrcodeBox").style.display = "none";
}

function comprar() {
    document.getElementById("qrcodeBox").style.display = "block";
}

function copiarPix() {
    const pix = document.getElementById("pix");
    pix.select();
    document.execCommand("copy");
    alert("PIX copiado!");
}