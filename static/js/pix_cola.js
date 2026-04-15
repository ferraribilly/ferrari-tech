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

    }, function (err) {
        console.error('Erro ao copiar: ', err);
    });
}