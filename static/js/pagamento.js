document.getElementById("btn-pagar").onclick = () => {

    document.getElementById("loading-pagamento").style.display = "flex";

    const nome = document.getElementById("nome").innerText;
    const sobrenome = document.getElementById("sobrenome").innerText;
    const cpf = document.getElementById("cpf").innerText;
    const email = document.getElementById("email").innerText;

    const url = `/payment_qrcode_pix/pagamento_pix/{{ usuario_id }}`
        + `?nome=${encodeURIComponent(nome)}`
        + `&sobrenome=${encodeURIComponent(sobrenome)}`
        + `&cpf=${encodeURIComponent(cpf)}`
        + `&email=${encodeURIComponent(email)}`
        + `&quantidade=${quantidade}`
        + `&lista_numeros=${encodeURIComponent(JSON.stringify(numerosSelecionados))}`;

    window.location.href = url;
};


document.getElementById("btn-preference").onclick = () => {

    document.getElementById("loading-pagamento").style.display = "flex";

    const nome = document.getElementById("nome").innerText;
    const sobrenome = document.getElementById("sobrenome").innerText;
    const cpf = document.getElementById("cpf").innerText;
    const email = document.getElementById("email").innerText;

    const url = `/compra/preference/pagamento_pix/{{ usuario_id }}`
        + `?nome=${encodeURIComponent(nome)}`
        + `&sobrenome=${encodeURIComponent(sobrenome)}`
        + `&cpf=${encodeURIComponent(cpf)}`
        + `&email=${encodeURIComponent(email)}`
        + `&quantidade=${quantidade}`
        + `&lista_numeros=${encodeURIComponent(JSON.stringify(numerosSelecionados))}`;

    window.location.href = url;
};