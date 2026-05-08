let quantidade = 0;

let valorUnitario = 0.60;

let numerosSelecionados = [];

let urlsGeradasNestaSessao = [];

let dotsInterval;

function startDots() {

    const dots = document.getElementById("dots");

    let count = 0;

    dotsInterval = setInterval(() => {

        count = (count + 1) % 4;

        dots.innerText = ".".repeat(count);

    }, 400);

}

function stopDots() {

    clearInterval(dotsInterval);

}

async function gerarBilhete() {

    const loading = document.getElementById("loading");

    const btn = document.querySelector(".btn-generate");

    loading.style.display = "block";

    startDots();

    btn.disabled = true;

    try {

        const table = document.querySelector('.input-numero');

        const bolas = table.querySelectorAll('.numero');

        let numero = '';

        let incompleto = false;

        bolas.forEach(bola => {

            let valor = bola.textContent.trim();

            valor = valor.replace(/\D/g, '');

            if (valor.length < 1 || valor.length > 2) {

                incompleto = true;

            }

            numero += valor;

        });

        if (incompleto) {

            alert("Preencha todas as 4 bolas com 1 ou 2 números cada bola sendo do 1 á 60.");

            stopDots();

            loading.style.display = "none";

            btn.disabled = false;

            return;

        }

        const usuario_id = document.getElementById("usuario_id").innerText;

        const nome = document.getElementById("nome").innerText;

        const cpf = document.getElementById("cpf").innerText;

        const email = document.getElementById("email").innerText;

        const paymentId = document.getElementById("payment_id")?.innerText || "aguardando";

        const valor = document.getElementById("valor")?.innerText || "1.25";

        const dataSort = document.getElementById("dataSort")?.innerText || "atingir meta 80%";

        const res = await fetch(`/gerar-bilhete/${usuario_id}`, {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                numero,

                nome,

                email,

                cpf

            })

        });

        const data = await res.json();

        if (data.img) {

            urlsGeradasNestaSessao.push(data.img);

            quantidade++;

            numerosSelecionados.push(numero);

            document.getElementById("total").innerText =
                (quantidade * valorUnitario).toFixed(2);

            // CALCULAR TOTAL BRUTO DO CARRINHO
            document.getElementById("total-bruto").innerText =
                (quantidade * valorUnitario).toFixed(2);    

            const container = document.getElementById("cards");

            const card = document.createElement("div");

            card.style.background = "#111";

            card.style.padding = "10px";

            card.style.borderRadius = "10px";

            card.style.marginTop = "10px";

            const img = document.createElement("img");

            img.src = data.img + "?t=" + new Date().getTime();

            img.style.width = "100%";

            img.style.borderRadius = "8px";

            card.appendChild(img);

            container.prepend(card);

            /* 🔥 AQUI FOI A ÚNICA ALTERAÇÃO */
            const lista = document.getElementById("lista-numeros");

            lista.innerHTML = "";

            numerosSelecionados.forEach(num => {

                const item = document.createElement("div");
                item.className = "item";

                item.innerHTML = `
                    <img src="https://res.cloudinary.com/dptprh0xk/image/upload/v1765238905/ticket_juifuh.png">
                    <div class="info">
                        <div class="nome">Bilhete N° ${num}</div>
                        <div class="detalhes">⏱ Pagamento Pendente</div>
                        <div class="preco">R$ ${valorUnitario.toFixed(2)}</div>
                    </div>
                `;

                lista.appendChild(item);

            });

        }

    } catch (e) {

        alert("Erro ao gerar bilhete");

    }

    stopDots();

    loading.style.display = "none";

    btn.disabled = false;

}

function cancelarTodosBilhetes() {

    const container = document.getElementById("cards");

    container.innerHTML = "";

    numerosSelecionados = [];

    quantidade = 0;

    document.getElementById("total").innerText = "0.00";

    const lista = document.getElementById("lista-numeros");

    lista.innerHTML = "";

}

function deletarTodosBilhetes() {

    const container = document.getElementById("cards");

    container.innerHTML = "";

    numerosSelecionados = [];

    quantidade = 0;

    document.getElementById("total").innerText = "0.00";

    const lista = document.getElementById("lista-numeros");

    lista.innerHTML = "";

}

const modal = document.getElementById('modal');

const confirmBtn = document.getElementById('confirmBtn');

const cancelBtn = document.getElementById('cancelBtn');

confirmBtn.addEventListener('click', () => modal.style.display = 'flex');

cancelBtn.addEventListener('click', async () => {

    startCancelando();

    const emailUsuario = document.getElementById("email").innerText;

    try {

        const res = await fetch("/cancelar-bilhetes_e_deletar_mongo_cloudinart", {

            method: "DELETE",

            headers: { "Content-Type": "application/json" },

            body: JSON.stringify({

                email: emailUsuario,

                urls: urlsGeradasNestaSessao

            })

        });

        const data = await res.json();

        if (data.sucesso) {

            deletarTodosBilhetes();

            urlsGeradasNestaSessao = [];

            modal.style.display = 'none';

        } else {

            alert("Erro ao cancelar: " + data.erro);

        }

    } catch (e) {

        alert("Erro na requisição");

    }

    stopCancelando();

});


// let quantidade = 0;

// let valorUnitario = 0.60;

// let numerosSelecionados = [];

// let urlsGeradasNestaSessao = [];

// let dotsInterval;

// function startDots() {
//     const dots = document.getElementById("dots");
//     let count = 0;

//     dotsInterval = setInterval(() => {
//         count = (count + 1) % 4;
//         dots.innerText = ".".repeat(count);
//     }, 400);
// }

// function stopDots() {
//     clearInterval(dotsInterval);
// }

// async function gerarBilhete() {

//     const loading = document.getElementById("loading");
//     const btn = document.querySelector(".btn-generate");

//     loading.style.display = "block";
//     startDots();
//     btn.disabled = true;

//     try {

//         const table = document.querySelector('.input-numero');
//         const bolas = table.querySelectorAll('.numero');

//         let numero = '';
//         let incompleto = false;

//         bolas.forEach(bola => {

//             let valor = bola.textContent.trim();
//             valor = valor.replace(/\D/g, '');

//             if (valor.length < 1 || valor.length > 2) {
//                 incompleto = true;
//             }

//             // ✔ CORREÇÃO: não força 01, 02, etc
//             numero += valor;

//         });

//         if (incompleto) {
//             alert("Preencha todas as 4 bolas com 1 ou 2 números cada bola sendo do 1 á 60.");
//             stopDots();
//             loading.style.display = "none";
//             btn.disabled = false;
//             return;
//         }

//         const usuario_id = document.getElementById("usuario_id").innerText;
//         const nome = document.getElementById("nome").innerText;
//         const cpf = document.getElementById("cpf").innerText;
//         const email = document.getElementById("email").innerText;

//         const paymentId = document.getElementById("payment_id")?.innerText || "aguardando";
//         const valor = document.getElementById("valor")?.innerText || "1.25";
//         const dataSort = document.getElementById("dataSort")?.innerText || "atingir meta 80%";

//         const res = await fetch(`/gerar-bilhete/${usuario_id}`, {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json"
//             },
//             body: JSON.stringify({
//                 numero,
//                 nome,
//                 email,
//                 cpf
//             })
//         });

//         const data = await res.json();

//         if (data.img) {

//             urlsGeradasNestaSessao.push(data.img);

//             quantidade++;
//             numerosSelecionados.push(numero);

//             document.getElementById("total").innerText =
//                 (quantidade * valorUnitario).toFixed(2);

//             const container = document.getElementById("cards");

//             const card = document.createElement("div");
//             card.style.background = "#111";
//             card.style.padding = "10px";
//             card.style.borderRadius = "10px";
//             card.style.marginTop = "10px";

//             const img = document.createElement("img");
//             img.src = data.img + "?t=" + new Date().getTime();
//             img.style.width = "100%";
//             img.style.borderRadius = "8px";

//             card.appendChild(img);
//             container.prepend(card);

//             const lista = document.getElementById("lista-numeros");
//             lista.innerHTML = "";

//             numerosSelecionados.forEach(num => {
//                 const item = document.createElement("div");
//                 item.innerText = num;
//                 item.style.color = "#f1eeee";
//                 item.style.fontWeight = "bold";
//                 lista.appendChild(item);
//             });
//         }

//     } catch (e) {
//         alert("Erro ao gerar bilhete");
//     }

//     stopDots();
//     loading.style.display = "none";
//     btn.disabled = false;
// }

// function cancelarTodosBilhetes() {
//     const container = document.getElementById("cards");
//     container.innerHTML = "";

//     numerosSelecionados = [];
//     quantidade = 0;

//     document.getElementById("total").innerText = "0.00";

//     const lista = document.getElementById("lista-numeros");
//     lista.innerHTML = "";
// }

// function deletarTodosBilhetes() {
//     const container = document.getElementById("cards");
//     container.innerHTML = "";

//     numerosSelecionados = [];
//     quantidade = 0;

//     document.getElementById("total").innerText = "0.00";

//     const lista = document.getElementById("lista-numeros");
//     lista.innerHTML = "";
// }

// const modal = document.getElementById('modal');
// const confirmBtn = document.getElementById('confirmBtn');
// const cancelBtn = document.getElementById('cancelBtn');

// confirmBtn.addEventListener('click', () => modal.style.display = 'flex');

// cancelBtn.addEventListener('click', async () => {

//     startCancelando(); // 🔥 INICIA ANIMAÇÃO

//     const emailUsuario = document.getElementById("email").innerText;

//     try {

//         const res = await fetch("/cancelar-bilhetes_e_deletar_mongo_cloudinart", {
//             method: "DELETE",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({
//                 email: emailUsuario,
//                 urls: urlsGeradasNestaSessao
//             })
//         });

//         const data = await res.json();

//         if (data.sucesso) {
//             deletarTodosBilhetes();
//             urlsGeradasNestaSessao = [];
//             modal.style.display = 'none';
//         } else {
//             alert("Erro ao cancelar: " + data.erro);
//         }

//     } catch (e) {
//         alert("Erro na requisição");
//     }

//     stopCancelando(); // 🔥 FINALIZA ANIMAÇÃO
// });



