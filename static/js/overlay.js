// PEGAR ELEMENTOS UMA VEZ SÓ
const cancelandoOverlay = document.getElementById("cancelandoOverlay");
const cancelandoTexto = document.getElementById("cancelandoTexto");

let cancelandoInterval = null;

function startCancelando() {
    cancelandoOverlay.style.display = "flex";

    let dots = 0;

    // evita duplicar interval
    if (cancelandoInterval) clearInterval(cancelandoInterval);

    cancelandoInterval = setInterval(() => {
        dots = (dots + 1) % 4;
        cancelandoTexto.innerText = "Cancelando, aguarde" + ".".repeat(dots);
    }, 400);
}

function stopCancelando() {
    cancelandoOverlay.style.display = "none";
    clearInterval(cancelandoInterval);
    cancelandoInterval = null;
}

