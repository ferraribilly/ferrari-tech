document.getElementById('copy').addEventListener('click', copyText);
document.getElementById('copy-mobile').addEventListener('click', copyText);

function copyText() {
    var qrcodeText = document.getElementById('qrcode-text');
    var copiedCodeBox = document.getElementById('copied-code');

    navigator.clipboard.writeText(qrcodeText.textContent).then(function () {
        // Efeito de blur e mostrar mensagem
        qrcodeText.style.filter = 'blur(1px)';
        copiedCodeBox.style.visibility = 'visible';
        copiedCodeBox.style.opacity = '0.9';
        copiedCodeBox.style.transition = 'all 0.3s';

        setTimeout(function () {
            qrcodeText.style.filter = '';
            copiedCodeBox.style.visibility = '';
            copiedCodeBox.style.opacity = '';
        }, 5000);

        // Redirecionar após copiar
        var id = qrcodeText.dataset.id; // Se você tiver o ID armazenado no data-id
        window.location.href = '/pendente?id=' + usuario_Id;
    });
}