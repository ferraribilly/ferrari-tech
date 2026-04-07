// PAGAMENTO QRCODE PIX
document.getElementById("btn-pagar").onclick = () => {

    const nome = document.getElementById("nome").innerText;
    const cpf = document.getElementById("cpf").innerText;
    const email = document.getElementById("email").innerText;

    const url = `/payment_qrcode_pix/pagamento_pix/{{ usuario_id }}`
        + `?nome=${encodeURIComponent(nome)}`
        + `&cpf=${encodeURIComponent(cpf)}`
        + `&email=${encodeURIComponent(email)}`
        + `&quantidade=${quantidade}`;

    window.location.href = url;
};

// PAGAMENTO PREFERENCE MERCADO PAGO
document.getElementById("btn-preference").onclick = () => {

    const nome = document.getElementById("nome").innerText;
    const cpf = document.getElementById("cpf").innerText;
    const email = document.getElementById("email").innerText;

    const url = `/compra/preference/pagamento_pix/{{ usuario_id }}`
        + `?nome=${encodeURIComponent(nome)}`
        + `&cpf=${encodeURIComponent(cpf)}`
        + `&email=${encodeURIComponent(email)}`
        + `&quantidade=${quantidade}`;

    window.location.href = url;
};


var usuario_Id = "{{ usuario_id }}";



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

var paymentId = "{{ payment_id }}";
var usuario_Id = "{{ usuario_id }}";
var socket = io(window.location.origin);

socket.on("connect", function () {
    socket.emit("join_payment", { payment_id: paymentId });
});

socket.on("payment_update", function (data) {
    if (data.payment_id !== paymentId) return;

    var div = document.getElementById("notifications");
    var p = document.createElement("p");

    if (data.status === "approved") {
        p.style.color = "green";
        p.innerText = "✅ Pagamento aprovado com sucesso!";
        div.innerHTML = "";
        div.appendChild(p);

        setTimeout(function () {
            
            window.location.href = `/aprovado?id=${usuario_Id}`;
        }, 3000);

    } else {
        p.style.color = "red";
        p.innerText = "❌ Pagamento recusado!";
        div.innerHTML = "";
        div.appendChild(p);

        setTimeout(function () {
            window.location.href = `/recusado?id=${usuario_Id}`;
        }, 3000);
    }
});




