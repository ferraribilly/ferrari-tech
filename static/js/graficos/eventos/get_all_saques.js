// ==========================================
// HISTORICO MENSAGENS SAQUES PELOS USUARIOS
// ==========================================
async function carregarMensagensSaques(){

    try {

        const response = await fetch(
            '/listar_mensagens_saques'
        );

        const data = await response.json();

        mensagens.innerHTML = '';

        data.mensagens.forEach(msg => {

            socket.emit(
                "nova_mensagem_saque",
                msg
            );

        });

    } catch(err){

        console.log(err);
    }

}

document.addEventListener(
    "DOMContentLoaded",
    carregarMensagensSaques
);