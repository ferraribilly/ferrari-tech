const openVideo = document.getElementById("openVideo");
const mainCard = document.getElementById("mainCard");
const videoCard = document.getElementById("videoCard");
const backBtn = document.getElementById("backToMenu");

openVideo.onclick = () => {
    mainCard.style.display = "none";
    videoCard.style.display = "block";
};

backBtn.onclick = () => {
    videoCard.style.display = "none";
    mainCard.style.display = "block";
};

const helpBtn = document.getElementById('helpBtn');
    const helpModal = document.getElementById('helpModal');
    const closeModal = document.getElementById('closeModal');

    // Abrir modal
    helpBtn.addEventListener('click', () => {
        helpModal.style.display = 'flex';
    });

    // Fechar modal
    closeModal.addEventListener('click', () => {
        helpModal.style.display = 'none';
    });

    // Fechar clicando fora do card
    window.addEventListener('click', (e) => {
        if (e.target === helpModal) {
            helpModal.style.display = 'none';
        }
    });

    document.addEventListener("DOMContentLoaded", function() {
    const banner = document.getElementById('cookie-banner');
    const acceptBtn = document.getElementById('accept-cookies');

    // Verifica se o usuário já aceitou
    if (!localStorage.getItem('cookiesAccepted')) {
        // Mostra o banner após 1 segundo
        setTimeout(() => {
            banner.classList.add('show');
        }, 1000);
    }

    // Ação ao clicar no botão
    acceptBtn.addEventListener('click', () => {
        localStorage.setItem('cookiesAccepted', 'true');
        banner.classList.remove('show');
    });
});
    



