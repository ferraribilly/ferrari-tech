const canvas = document.getElementById('card');
const ctx = canvas.getContext('2d');
const audioWin = document.getElementById('win-audio');

let raspado = false;
// Substitua a linha antiga por esta:
let raspadinhas = window.totalQuantidadeRaspadinhas;

// Prontinho! A variável 'raspadinhas' agora tem o número correto vindo do banco.
console.log("Quantidade do banco:", raspadinhas);
 
let totalGanho = 0;
let premioAtual = null;





// =========================
// INIT
// =========================
function init() {
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = '#888';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#fff';
    ctx.font = '24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Raspe aqui', canvas.width / 2, canvas.height / 2 + 8);
    raspado = false;
}

// =========================
// RASPAR
// =========================
function scratch(e) {
    if (raspadinhas <= 0 && !raspado) return;
    e.preventDefault();

    const rect = canvas.getBoundingClientRect();
    const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
    const y = (e.touches ? e.touches[0].clientY : e.clientY) - rect.top;

    ctx.globalCompositeOperation = 'destination-out';
    ctx.beginPath();
    ctx.arc(x, y, 20, 0, Math.PI * 2);
    ctx.fill();

    verificarRaspagem();
}

function verificarRaspagem() {
    if (raspado) return;

    const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    let transparentes = 0;
    for (let i = 3; i < pixels.length; i += 4) {
        if (pixels[i] === 0) {
            transparentes++;
        }
    }
    const porcentagem = transparentes / (canvas.width * canvas.height);

    if (porcentagem > 0.65) {
        raspado = true;
        raspadinhas--;

        fetch('/raspadinha/resultado', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_premio: premioAtual ? premioAtual.id_premio : null,
                usuario_id: typeof usuario_id === 'object' ? '' : usuario_id 
            })
        })
        .then(res => res.json())
        .then(dadosServidor => {
            if (dadosServidor.error) return;

            totalGanho += Number(dadosServidor.valorNumerico);
            
            const elementoQtd = document.getElementById('qtd-rsp');
            if (elementoQtd) elementoQtd.innerText = raspadinhas;

            const elementoValor = document.getElementById('valor-total');

            if (elementoValor) {

                // PEGA SOMENTE O GANHO ATUAL
                const valorAtual = Number(dadosServidor.valorNumerico || 0);

                elementoValor.innerText =
                    "R$ " + valorAtual.toFixed(2).replace(".", ",");

                // limpa timeout anterior
                clearTimeout(window.timeoutValorTotal);

                // limpa depois
                window.timeoutValorTotal = setTimeout(() => {

                    elementoValor.innerText = "R$ 0,00";

                }, 5000);
            }

            // ATUALIZAÇÃO DO SALDO EM TEMPO REAL ATIVADA AQUI
            if (dadosServidor && dadosServidor.novoSaldoTexto) {
                const elementoSaldo = document.getElementById('saldo-valor');
                if (elementoSaldo) {
                    elementoSaldo.innerText = dadosServidor.novoSaldoTexto;
                }
            }

            // =========================
            // WIN OVERLAY
            // =========================
            const winOverlay = document.getElementById('win-overlay');
            if (winOverlay) winOverlay.style.display = 'flex';

            const winAmount = document.getElementById('win-amount');
            if (winAmount) winAmount.innerText = dadosServidor.valorTexto;

            const winImage = document.getElementById('win-image');
            if (winImage && premioAtual) winImage.src = premioAtual.imagem;

            if (audioWin) {
                audioWin.currentTime = 0;
                audioWin.play().catch(err => console.log("Áudio bloqueado pelo navegador"));
            }

            if (typeof confetti === 'function') {
                confetti({
                    particleCount: 250,
                    spread: 180,
                    origin: { y: 0.6 }
                });
            }

            if (raspadinhas <= 0) {
                const btnNew = document.getElementById('new-btn');
                if (btnNew) {
                    btnNew.disabled = true;
                    btnNew.innerText = '0';
                }
            }

            setTimeout(() => {
                if (winOverlay) winOverlay.style.display = 'none';
            }, 3000);
        })
        .catch(err => console.error("Erro ao processar resultado:", err));
    }
}
// =========================
// EVENTOS CANVAS
// =========================
canvas.addEventListener('mousedown', () => {
    canvas.addEventListener('mousemove', scratch);
});

canvas.addEventListener('mouseup', () => {
    canvas.removeEventListener('mousemove', scratch);
});

canvas.addEventListener('touchstart', (e) => {
    canvas.addEventListener('touchmove', scratch);
}, { passive: false });

canvas.addEventListener('touchend', () => {
    canvas.removeEventListener('touchmove', scratch);
});

// =========================
// RESET CARD
// =========================
function resetCard() {
    if (raspadinhas <= 0) return;

    const cardElement = document.querySelector('.scratch-card');
    if (cardElement) {
        cardElement.classList.remove('slide-in');
        cardElement.classList.add('slide-out');
    }

    setTimeout(() => {
        fetch('/raspadinha/novo')
        .then(res => res.json())
        .then(dados => {
            premioAtual = {
                id_premio: dados.id_premio,
                imagem: dados.imagem
            };

            const prizeImg = document.getElementById('prize-image');
            if (prizeImg) prizeImg.src = premioAtual.imagem;

            init();

            if (cardElement) {
                cardElement.classList.remove('slide-out');
                cardElement.style.transform = "translateX(150%)";
                void cardElement.offsetWidth;
                cardElement.classList.add('slide-in');
            }
        })
        .catch(err => {
            console.error("Erro ao carregar nova raspadinha:", err);
            init(); // Força o carregamento do canvas mesmo se a rota falhar
        });
    }, 500);
}

// =========================
// SAQUE
// =========================
function abrirSaques() {
    document.getElementById('saques-overlay').style.display = 'flex';
}

function fecharSaques() {
    document.getElementById('saques-overlay').style.display = 'none';
}

function solicitarSaque() {
    const valorInput = document.getElementById('valor-saque').value;
    const valor = parseFloat(valorInput);

    if (isNaN(valor) || valor <= 0) {
        alert('Informe um valor válido!');
        return;
    }

    const idDoUsuario = typeof usuario_id === 'object' || !usuario_id 
        ? window.location.pathname.split('/')[2] 
        : usuario_id;

    fetch('/saque', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ valor: valor, usuario_id: idDoUsuario })
    })
    .then(res => res.json())
    .then(dados => {
        if (dados.erro) {
            alert(dados.erro);
            return;
        }

        totalGanho = Number(dados.ganhos);
        const elementoValor = document.getElementById('valor-total');
        if (elementoValor) elementoValor.innerText = "R$ " + totalGanho.toFixed(2).replace(".", ",");

        // --- INSERIDO: ATUALIZAÇÃO DO SALDO DO TOPO EM TEMPO REAL NO SAQUE ---
        const elementoSaldo = document.getElementById('saldo-valor');
        if (elementoSaldo) {
            elementoSaldo.innerText = "R$ " + totalGanho.toFixed(2).replace(".", ",");
        }
        
        // Limpa o input após o saque concluído com sucesso
        const inputSaque = document.getElementById('valor-saque');
        if (inputSaque) inputSaque.value = '';

        alert('Saque realizado com sucesso');

        const loadingDiv = document.createElement('div');
        loadingDiv.id = "loading-saque";
        loadingDiv.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;z-index:9999;";
        loadingDiv.innerHTML = "⏳ Aguarde... estamos processando";
        document.body.appendChild(loadingDiv);

        const nome = document.getElementById('saque-nome').value;
        const cpf = document.getElementById('saque-cpf').value;
        const pix = document.getElementById('saque-pix').value;
        const dataHora = new Date().toLocaleString('pt-BR');

        const msg = `💰 SOLICITAÇÃO DE SAQUE 💰\n\n👤 Nome: ${nome}\n🪪 CPF: ${cpf}\n🏦 PIX: ${pix}\n💵 Valor: R$ ${valor.toFixed(2).replace('.', ',')}\n📅 Data/Hora: ${dataHora}`;
        const url = `https://wa.me/5527998031796?text=${encodeURIComponent(msg)}`;

        setTimeout(() => { window.open(url, "_blank"); }, 1500);
        setTimeout(() => { loadingDiv.remove(); }, 2000);
    })
    .catch(err => {
        alert('Erro ao conectar com o servidor!');
    });
}


// =========================
// ABAS LOGIN
// =========================
document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.auth-tab');
    const forms = document.querySelectorAll('.auth-form');

    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            forms.forEach(f => f.classList.remove('active'));
            tab.classList.add('active');
            if (forms[index]) forms[index].classList.add('active');
        });
    });
});

async function carregarMovimentacoes() {
    const res = await fetch('/movimentacoes');
    const data = await res.json();

    const entradas = document.getElementById('entradas-body');
    const saidas = document.getElementById('saidas-body');
    const ganhos = document.getElementById('valor-saque');

    if (entradas) {
        entradas.innerHTML = "";
        (data.entradas || []).forEach(e => {
            const valor = Number(e.valor || 0).toFixed(2).replace(".", ",");
            entradas.innerHTML += `
                <tr>
                    <td>${e.data}</td>
                    <td>${e.tipo}</td>
                    <td style="color:#00ff00;">R$ ${valor}</td>
                </tr>
            `;
        });
        if (!data.entradas || data.entradas.length === 0) {
            entradas.innerHTML = `<tr><td colspan="3">Nenhuma entrada</td></tr>`;
        }
    }

    if (saidas) {
        saidas.innerHTML = "";
        (data.saidas || []).forEach(s => {
            const valor = Number(s.valor || 0).toFixed(2).replace(".", ",");
            saidas.innerHTML += `
                <tr>
                    <td>${s.data}</td>
                    <td>${s.tipo}</td>
                    <td style="color:#ff4444;">R$ ${valor}</td>
                </tr>
            `;
        });
        if (!data.saidas || data.saidas.length === 0) {
            saidas.innerHTML = `<tr><td colspan="3">Nenhuma saída</td></tr>`;
        }
    }

    if (ganhos) {
        ganhos.value = Number(data.ganhos || 0).toFixed(2).replace(".", ",");
    }

    // 🔴 ISSO AQUI RESOLVE SEU PROBLEMA DO SALDO NÃO ATUALIZAR
    if (ganhos) {
        ganhos.value = Number(data.ganhos || 0).toFixed(2).replace(".", ",");
    }

}

// =========================
// ABA SAQUE
// =========================
function mudarAbaSaque(index) {
    const abas = document.querySelectorAll('.aba-saque-content');
    const botoes = document.querySelectorAll('.saques-card .auth-tab');

    abas.forEach((aba, i) => {
        aba.style.display = (i === index) ? 'block' : 'none';
        if (botoes[i]) botoes[i].classList.toggle('active', i === index);
    });
}

// =========================
// PIX
// =========================
function mudarAbaPix(index) {
    const slider = document.getElementById("buySlider");
    const tabs = document.querySelectorAll(".auth-tab");

    if (slider) slider.style.transform = `translateX(-${index * 50}%)`;
    tabs.forEach(tab => tab.classList.remove("active"));
    if (tabs[index]) tabs[index].classList.add("active");
}

// =========================
// OVERLAYS
// =========================
function abrirCompra() {
    document.getElementById('buy-overlay').style.display = 'flex';
}

function fecharCompra() {
    document.getElementById('buy-overlay').style.display = 'none';
}

function abrirPremios() {
    document.getElementById('prize-overlay').style.display = 'flex';
}

function fecharPremios() {
    document.getElementById('prize-overlay').style.display = 'none';
}




function abrirSuporte(){

    document.getElementById("modal-suporte").style.display = "flex";

}

function fecharSuporte(){

    document.getElementById("modal-suporte").style.display = "none";

}

function suporteCompra(){

    const nome = document.getElementById("nome")?.innerText || "Não informado";

    const cpf = document.getElementById("cpf")?.innerText || "Não informado";

    const msg =
`🛒 PROBLEMA NA COMPRA

👤 Nome: ${nome}
🪪 CPF: ${cpf}

Preciso suporte referente meu pagamento por favor.`;

    const url = `https://wa.me/5527998031796?text=${encodeURIComponent(msg)}`;

    window.open(url, "_blank");

}

function suporteSaque(){

    const nome = document.getElementById("nome")?.innerText || "Não informado";

    const cpf = document.getElementById("cpf")?.innerText || "Não informado";

    const msg =
`💰 PROBLEMA COM SAQUE

👤 Nome: ${nome}
🪪 CPF: ${cpf}

Preciso suporte referente meu saque por favor.`;

    const url = `https://wa.me/5527998031796?text=${encodeURIComponent(msg)}`;

    window.open(url, "_blank");

}

function falarAdministrador(){

    const nome = document.getElementById("nome")?.innerText || "Não informado";

    const cpf = document.getElementById("cpf")?.innerText || "Não informado";

    const msg =
`👨‍💻 FALAR COM ADMINISTRADOR

👤 Nome: ${nome}
🪪 CPF: ${cpf}

Preciso falar com administrador por favor.`;

    const url = `https://wa.me/5527998031796?text=${encodeURIComponent(msg)}`;

    window.open(url, "_blank");

}


function abrirdados(){

    document.getElementById("modal-dados").style.display = "flex";

}

function fechardados(){

    document.getElementById("modal-dados").style.display = "none";

}






// =========================
// START
// =========================
resetCard();
