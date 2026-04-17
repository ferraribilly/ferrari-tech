document.addEventListener("DOMContentLoaded", function () {

    const btn1 = document.getElementById('copy');
    const btn2 = document.getElementById('copy-mobile');

    if (btn1) btn1.addEventListener('click', copyText);
    if (btn2) btn2.addEventListener('click', copyText);

});

function copyText() {

    var qrcodeText = document.getElementById('qrcode-text');
    var copiedCodeBox = document.getElementById('copied-code');

    const text = qrcodeText.textContent;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(afterCopy);
    } else {
        const textarea = document.createElement("textarea");
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
        afterCopy();
    }

    function afterCopy() {

        qrcodeText.style.filter = 'blur(1px)';
        copiedCodeBox.style.visibility = 'visible';
        copiedCodeBox.style.opacity = '0.9';
        copiedCodeBox.style.transition = 'all 0.3s';

        setTimeout(function () {
            qrcodeText.style.filter = '';
            copiedCodeBox.style.visibility = '';
            copiedCodeBox.style.opacity = '';
        }, 5000);

        // CORREÇÃO AQUI
        const payment_id = document.getElementById("id-payment").innerText;

        setTimeout(function () {
            window.location.href = "/aguardando_pagamento/" + payment_id;
        }, 3000);
    }
}