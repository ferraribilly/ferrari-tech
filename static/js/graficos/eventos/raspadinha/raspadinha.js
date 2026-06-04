const canvas = document.getElementById('card');
const ctx = canvas.getContext('2d');
const audioWin = document.getElementById('win-audio');

let raspado = false;

// BLOQUEIA TROCA DURANTE RASPAGEM
let raspandoAgora = false;

// Substitua a linha antiga por esta:
let raspadinhas = window.totalQuantidadeRaspadinhas;

// Prontinho! A variável 'raspadinhas' agora tem o número correto vindo do banco.
console.log("Quantidade do banco:", raspadinhas);

let totalGanho = 0;
let premioAtual = null;


// =========================
// RESTAURA ESTADO
// =========================
const raspagemSalva = localStorage.getItem("raspandoAgora");

if (raspagemSalva === "1") {

    raspandoAgora = true;

    const premioSalvo = localStorage.getItem("premioAtual");

    if (premioSalvo) {

        premioAtual = JSON.parse(premioSalvo);

        const prizeImg = document.getElementById('prize-image');

        if (prizeImg && premioAtual.imagem) {
            prizeImg.src = premioAtual.imagem;
        }
    }

    // RESTAURA CANVAS RASPADO
    const canvasSalvo = localStorage.getItem("canvasRaspado");

    if (canvasSalvo) {

        const img = new Image();

        img.onload = function () {

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            ctx.drawImage(img, 0, 0);
        };

        img.src = canvasSalvo;
    }
}



// =========================
// SALVA ESTADO
// =========================
function salvarEstadoRaspagem() {

    localStorage.setItem(
        "raspandoAgora",
        raspandoAgora ? "1" : "0"
    );

    if (premioAtual) {

        localStorage.setItem(
            "premioAtual",
            JSON.stringify(premioAtual)
        );
    }

    // SALVA O CANVAS RASPADO
    localStorage.setItem(
        "canvasRaspado",
        canvas.toDataURL()
    );
}





// =========================
// INIT
// =========================
function init() {

    // NÃO RESETA SE ESTIVER RASPANDO
    if (localStorage.getItem("raspandoAgora") === "1") {
        return;
    }

    ctx.globalCompositeOperation = 'source-over';

    ctx.fillStyle = '#888';

    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#fff';

    ctx.font = '24px Arial';

    ctx.textAlign = 'center';

    ctx.fillText(
        'Raspe aqui',
        canvas.width / 2,
        canvas.height / 2 + 8
    );

    raspado = false;

    if (!localStorage.getItem("raspandoAgora")) {
        raspandoAgora = false;
    }
}




// =========================
// RASPAR
// =========================
function scratch(e) {

    // MARCA QUE COMEÇOU
    raspandoAgora = true;

    if (raspadinhas <= 0 && !raspado) return;

    e.preventDefault();

    const rect = canvas.getBoundingClientRect();

    const x =
        (e.touches ? e.touches[0].clientX : e.clientX)
        - rect.left;

    const y =
        (e.touches ? e.touches[0].clientY : e.clientY)
        - rect.top;

    ctx.globalCompositeOperation = 'destination-out';

    ctx.beginPath();

    ctx.arc(x, y, 20, 0, Math.PI * 2);

    ctx.fill();

    // SALVA APÓS RASPAR
    salvarEstadoRaspagem();

    verificarRaspagem();
}




function verificarRaspagem() {

    if (raspado) return;

    const pixels =
        ctx.getImageData(
            0,
            0,
            canvas.width,
            canvas.height
        ).data;

    let transparentes = 0;

    for (let i = 3; i < pixels.length; i += 4) {

        if (pixels[i] === 0) {
            transparentes++;
        }
    }

    const porcentagem =
        transparentes / (canvas.width * canvas.height);

    if (porcentagem > 0.65) {

        raspado = true;

        raspadinhas--;

        fetch('/raspadinha/resultado', {

            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify({

                id_premio:
                    premioAtual
                    ? premioAtual.id_premio
                    : null,

                usuario_id:
                    typeof usuario_id === 'object'
                    ? ''
                    : usuario_id
            })

        })

        .then(res => res.json())

        .then(dadosServidor => {

            if (dadosServidor.error) return;

            totalGanho +=
                Number(dadosServidor.valorNumerico);

            const elementoQtd =
                document.getElementById('qtd-rsp');

            if (elementoQtd) {

                elementoQtd.innerText = raspadinhas;
            }

            const elementoValor =
                document.getElementById('valor-total');

            if (elementoValor) {

                const valorAtual =
                    Number(
                        dadosServidor.valorNumerico || 0
                    );

                elementoValor.innerText =
                    "R$ "
                    + valorAtual
                        .toFixed(2)
                        .replace(".", ",");

                clearTimeout(window.timeoutValorTotal);

                window.timeoutValorTotal =
                    setTimeout(() => {

                        elementoValor.innerText =
                            "R$ 0,00";

                    }, 5000);
            }

            if (
                dadosServidor
                &&
                dadosServidor.novoSaldoTexto
            ) {

                const elementoSaldo =
                    document.getElementById('saldo-valor');

                if (elementoSaldo) {

                    elementoSaldo.innerText =
                        dadosServidor.novoSaldoTexto;
                }
            // FUNDO PERSONALIZADO PARA CADA PRÊMIO

            const fundosPremios = {
                "R$ 0,00": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780453819/alexas_fotos-halloween-959049_1920_kcts9z.png",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780453819/alexas_fotos-halloween-959049_1920_kcts9z.png"
                },

                "R$ 0,05": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1765412810/pngwing.com_5_x9e2sp.png",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1778712310/1778711818646_obyfa1.png"
                },

                "R$ 0,10": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780495301/fiverr_3dillustration___watercolor_3DWatercolorlllustration___FlowerVase_SpringFlowers_Delicate___Shadows___SoftSunlight_VisuallyStunning___Immersive3DRender_Cinematic___ArtisticPanache_cblwth.jpg",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1765234429/pngwing.com_1_pgr4aj.png"
                },

                "R$ 0,25": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780495302/conceito-de-fundo-de-luzes-de-velocidade_vdrpwr.png",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1765203729/pngwing.com_7_jeodlf.png"
                },

                "R$ 0,30": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780495301/WARP_CASINO_%E0%B8%9A%E0%B8%B2%E0%B8%84%E0%B8%B2%E0%B8%A3%E0%B9%88%E0%B8%B2_%E0%B8%84%E0%B8%B2%E0%B8%AA%E0%B8%B4%E0%B9%82%E0%B8%99%E0%B8%AD%E0%B8%AD%E0%B8%99%E0%B9%84%E0%B8%A5%E0%B8%99%E0%B9%8C_%E0%B8%AA%E0%B8%A5%E0%B9%87%E0%B8%AD%E0%B8%95_%E0%B9%84%E0%B8%94%E0%B9%89%E0%B9%80%E0%B8%87%E0%B8%B4%E0%B8%99%E0%B8%88%E0%B8%A3%E0%B8%B4%E0%B8%87_%E0%B8%A1%E0%B8%B2%E0%B8%95%E0%B8%A3%E0%B8%90%E0%B8%B2%E0%B8%99%E0%B9%82%E0%B8%A5%E0%B8%81_ct6b1h.jpg",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1778704207/1778632824626_hzdcgx.png"
                },

                "R$ 0,50": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496672/%D0%94%D0%B5%D0%BD%D0%B5%D0%B6%D0%BD%D1%8B%D0%B5_%D0%B7%D0%B0%D1%81%D1%82%D0%B0%D0%B2%D0%BA%D0%B8__%D0%9E%D0%B1%D0%BE%D0%B8_%D1%83%D1%81%D0%BF%D0%B5%D1%85_%D0%B8%D0%B7%D0%BE%D0%B1%D0%B8%D0%BB%D0%B8%D0%B5_aaabmy.jpg",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496672/%D0%94%D0%B5%D0%BD%D0%B5%D0%B6%D0%BD%D1%8B%D0%B5_%D0%B7%D0%B0%D1%81%D1%82%D0%B0%D0%B2%D0%BA%D0%B8__%D0%9E%D0%B1%D0%BE%D0%B8_%D1%83%D1%81%D0%BF%D0%B5%D1%85_%D0%B8%D0%B7%D0%BE%D0%B1%D0%B8%D0%BB%D0%B8%D0%B5_aaabmy.jpg"
                } ,
                "R$ 1,00": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1778788561/HcUcY_jxukft.png",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1778788561/HcUcY_jxukft.png"
                },
                "R$ 5,00": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496951/fd9cb2fe-4fbe-4156-a7ee-2ce3da92292a_zjuun0.jpg",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496951/fd9cb2fe-4fbe-4156-a7ee-2ce3da92292a_zjuun0.jpg"
                },
                "R$ 10,00": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496951/fd9cb2fe-4fbe-4156-a7ee-2ce3da92292a_zjuun0.jpg",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496951/fd9cb2fe-4fbe-4156-a7ee-2ce3da92292a_zjuun0.jpg"
                },
                "R$ 20,00": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496673/ai_%E0%B8%A7%E0%B8%AD%E0%B8%A5%E0%B8%AA%E0%B8%A7%E0%B8%A2%E0%B9%86%E0%B8%A3%E0%B8%A7%E0%B8%A2%E0%B9%86_shbwr7.jpg",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496951/fd9cb2fe-4fbe-4156-a7ee-2ce3da92292a_zjuun0.jpg"
                },
                "R$ 30,00": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496951/fd9cb2fe-4fbe-4156-a7ee-2ce3da92292a_zjuun0.jpg",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496672/%D0%94%D0%B5%D0%BD%D0%B5%D0%B6%D0%BD%D1%8B%D0%B5_%D0%B7%D0%B0%D1%81%D1%82%D0%B0%D0%B2%D0%BA%D0%B8__%D0%9E%D0%B1%D0%BE%D0%B8_%D1%83%D1%81%D0%BF%D0%B5%D1%85_%D0%B8%D0%B7%D0%BE%D0%B1%D0%B8%D0%BB%D0%B8%D0%B5_aaabmy.jpg"
                },
                "R$ 50,00": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496672/%D0%94%D0%B5%D0%BD%D0%B5%D0%B6%D0%BD%D1%8B%D0%B5_%D0%B7%D0%B0%D1%81%D1%82%D0%B0%D0%B2%D0%BA%D0%B8__%D0%9E%D0%B1%D0%BE%D0%B8_%D1%83%D1%81%D0%BF%D0%B5%D1%85_%D0%B8%D0%B7%D0%BE%D0%B1%D0%B8%D0%BB%D0%B8%D0%B5_aaabmy.jpg",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496672/%D0%94%D0%B5%D0%BD%D0%B5%D0%B6%D0%BD%D1%8B%D0%B5_%D0%B7%D0%B0%D1%81%D1%82%D0%B0%D0%B2%D0%BA%D0%B8__%D0%9E%D0%B1%D0%BE%D0%B8_%D1%83%D1%81%D0%BF%D0%B5%D1%85_%D0%B8%D0%B7%D0%BE%D0%B1%D0%B8%D0%BB%D0%B8%D0%B5_aaabmy.jpg"
                },
                "R$ 100,00": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780495301/fa%C3%A7a_essa_ora%C3%A7%C3%A3o_lc4uvy.jpg",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496672/%D0%94%D0%B5%D0%BD%D0%B5%D0%B6%D0%BD%D1%8B%D0%B5_%D0%B7%D0%B0%D1%81%D1%82%D0%B0%D0%B2%D0%BA%D0%B8__%D0%9E%D0%B1%D0%BE%D0%B8_%D1%83%D1%81%D0%BF%D0%B5%D1%85_%D0%B8%D0%B7%D0%BE%D0%B1%D0%B8%D0%BB%D0%B8%D0%B5_aaabmy.jpg"
                },
                "R$ 200,00": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780495301/fa%C3%A7a_essa_ora%C3%A7%C3%A3o_lc4uvy.jpg",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780496672/%D0%94%D0%B5%D0%BD%D0%B5%D0%B6%D0%BD%D1%8B%D0%B5_%D0%B7%D0%B0%D1%81%D1%82%D0%B0%D0%B2%D0%BA%D0%B8__%D0%9E%D0%B1%D0%BE%D0%B8_%D1%83%D1%81%D0%BF%D0%B5%D1%85_%D0%B8%D0%B7%D0%BE%D0%B1%D0%B8%D0%BB%D0%B8%D0%B5_aaabmy.jpg"
                },
                "R$ 1000,00": {
                    overlay: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780495301/fa%C3%A7a_essa_ora%C3%A7%C3%A3o_lc4uvy.jpg",
                    content: "https://res.cloudinary.com/dptprh0xk/image/upload/v1780495301/3dc609c2-7856-4323-964f-d623fc593456_b4pjzr.jpg"
                }                                                                                                                 
            };

            const premioConfig =
                fundosPremios[dadosServidor.valorTexto];

            const winOverlay =
                document.getElementById('win-overlay');

            const winContent =
                document.querySelector('.win-content');

            if (premioConfig) {

                if (winOverlay) {
                    winOverlay.style.backgroundImage =
                        `url('${premioConfig.overlay}')`;
                }

                if (winContent) {
                    winContent.style.backgroundImage =
                        `url('${premioConfig.content}')`;
                }

            }                
            }

            const winOverlay =
                document.getElementById('win-overlay');

            if (winOverlay) {

                winOverlay.style.display = 'flex';
            }

            const winAmount =
                document.getElementById('win-amount');

            if (winAmount) {

                winAmount.innerText =
                    dadosServidor.valorTexto;
            }

            const winImage =
                document.getElementById('win-image');

            if (winImage && premioAtual) {

                winImage.src = premioAtual.imagem;
            }
            const audiosPremios = {
                "R$ 0,00": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780431737/placidplace-spooky-halloween-effects-with-thunder-121665_nrho8n.mp3",
                "R$ 0,05": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/whoosh-impact-coin-drop-transition-bosnow-result-window-pop-ringing-triumphant-1-0m08s_i8ccxx.mp3",
                "R$ 0,10": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/whoosh-impact-coin-drop-transition-bosnow-result-window-pop-ringing-triumphant-1-0m08s_i8ccxx.mp3",
                "R$ 0,25": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/whoosh-impact-coin-drop-transition-bosnow-result-window-pop-ringing-triumphant-1-0m08s_i8ccxx.mp3",
                "R$ 0,30": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/whoosh-impact-coin-drop-transition-bosnow-result-window-pop-ringing-triumphant-1-0m08s_i8ccxx.mp3",
                "R$ 0,50": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/whoosh-impact-coin-drop-transition-bosnow-result-window-pop-ringing-triumphant-1-0m08s_i8ccxx.mp3",
                "R$ 1,00": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/meme-party-music-loop-bosnow-1-00-03_avovml.mp3",
                "R$ 5,00": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/meme-party-music-loop-bosnow-1-00-03_avovml.mp3",
                "R$ 10,00": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/meme-party-music-loop-bosnow-1-00-03_avovml.mp3",
                "R$ 20,00": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/meme-party-music-loop-bosnow-1-00-03_avovml.mp3",
                "R$ 30,00": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/meme-party-music-loop-bosnow-1-00-03_avovml.mp3",
                "R$ 50,00": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/meme-party-music-loop-bosnow-1-00-03_avovml.mp3",
                "R$ 100,00": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/meme-party-music-loop-bosnow-1-00-03_avovml.mp3",
                "R$ 200,00": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/meme-party-music-loop-bosnow-1-00-03_avovml.mp3",
                "R$ 1000,00": "https://res.cloudinary.com/dptprh0xk/video/upload/v1780494533/meme-party-music-loop-bosnow-1-00-03_avovml.mp3"
            };

            if (window.audioPremioAtual) {
                window.audioPremioAtual.pause();
                window.audioPremioAtual.currentTime = 0;
            }

            const audioPremio =
                audiosPremios[dadosServidor.valorTexto];

            if (audioPremio) {

                window.audioPremioAtual =
                    new Audio(audioPremio);

                window.audioPremioAtual.volume = 1;

                window.audioPremioAtual.play().catch(err =>
                    console.log(
                        "Áudio bloqueado pelo navegador"
                    )
                );

            }

            if (typeof confetti === 'function') {

                confetti({
                    particleCount: 250,
                    spread: 180,
                    origin: { y: 0.6 }
                });
            }

            if (raspadinhas <= 0) {

                const btnNew =
                    document.getElementById('new-btn');

                if (btnNew) {

                    btnNew.disabled = true;

                    btnNew.innerText = '0';
                }
            }

            setTimeout(() => {

                if (winOverlay) {

                    winOverlay.style.display = 'none';
                }

                // LIBERA SOMENTE DEPOIS QUE TERMINOU
                raspandoAgora = false;

                localStorage.removeItem(
                    "raspandoAgora"
                );

                localStorage.removeItem(
                    "premioAtual"
                );

                localStorage.removeItem(
                    "canvasRaspado"
                );

            }, 3000);

        })

        .catch(err =>
            console.error(
                "Erro ao processar resultado:",
                err
            )
        );
    }
}




// =========================
// EVENTOS CANVAS
// =========================
canvas.addEventListener('mousedown', () => {

    canvas.addEventListener('mousemove', scratch);
});

canvas.addEventListener('mouseup', () => {

    canvas.removeEventListener(
        'mousemove',
        scratch
    );
});

canvas.addEventListener('touchstart', (e) => {

    canvas.addEventListener(
        'touchmove',
        scratch
    );

}, { passive: false });

canvas.addEventListener('touchend', () => {

    canvas.removeEventListener(
        'touchmove',
        scratch
    );
});




// =========================
// RESET CARD
// =========================
function resetCard() {

    // BLOQUEIA TROCA ENQUANTO RASPA
    if (raspandoAgora) {

        const statusBox =
            document.getElementById('status-box');

        if (statusBox) {

            const aviso =
                document.createElement('div');

            aviso.innerText =
                "⚠️ Termine de raspar a atual";

            aviso.style.color = "red";

            aviso.style.fontWeight = "bold";

            aviso.style.margin = "5px 0";

            statusBox.prepend(aviso);

            setTimeout(() => {

                aviso.remove();

            }, 3000);
        }

        return;
    }

    if (raspadinhas <= 0) return;

    const cardElement =
        document.querySelector('.scratch-card');

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

            const prizeImg =
                document.getElementById('prize-image');

            if (prizeImg) {

                prizeImg.src = premioAtual.imagem;
            }

            // LIMPA ESTADO ANTIGO
            localStorage.removeItem("canvasRaspado");

            localStorage.removeItem("premioAtual");

            localStorage.removeItem("raspandoAgora");

            init();

            if (cardElement) {

                cardElement.classList.remove(
                    'slide-out'
                );

                cardElement.style.transform =
                    "translateX(150%)";

                void cardElement.offsetWidth;

                cardElement.classList.add(
                    'slide-in'
                );
            }

        })

        .catch(err => {

            console.error(
                "Erro ao carregar nova raspadinha:",
                err
            );

            init();

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

        alert('Vamos será direcionado sala saque!');

        const loadingDiv = document.createElement('div');
        loadingDiv.id = "loading-saque";
        loadingDiv.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;z-index:9999;";
        loadingDiv.innerHTML = "⏳ Aguarde... estamos processando";
        document.body.appendChild(loadingDiv);


        const nome = document.getElementById('saque-nome').value;
        const cpf = document.getElementById('saque-cpf').value;
        const pix = document.getElementById('saque-pix').value;
        const usuarioId = document.getElementById('usuario_id').innerText;
        const dataHora = new Date().toLocaleString('pt-BR');

        // MASCARA CPF
        const cpfMascarado = cpf
            .replace(/\D/g, '')
            .replace(/(\d{3})\d{3}(\d{3})(\d{2})/, '$1.***.$2-**');

        const msg = `💰 SOLICITAÇÃO DE SAQUE 💰
        🆔 ID: ${usuarioId}
        👤 Nome: ${nome}
        🪪 CPF: ${cpfMascarado}
        🏦 PIX: ${pix}
        💵 Valor: R$ ${valor.toFixed(2).replace('.', ',')}
        📅 Data/Hora: ${dataHora}`;

        const usuario_id = document.getElementById("usuario_id").textContent.trim();

        const url = `/chat/usuario/${usuario_id}/6a1cd78b784f32efa3666ba3?text=${encodeURIComponent(msg)}`;
        
        

        setTimeout(() => { window.open(url, "_blank"); }, 1500);
        setTimeout(() => { loadingDiv.remove(); }, 2000);
    })
    .catch(err => {
        alert('Erro ao conectar com o servidor!');
    });
}




async function fazerTransferencia() {
const valor = document
    .getElementById('valor-transferencia')
    .value
    .replace(",", ".");

const favorecido = document
    .getElementById('favorecido')
    .value
    .trim();

const res = await fetch('/transferencia', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        valor,
        favorecido
    })
});

const data = await res.json();

if (data.success) {

    alert(data.mensagem);

    document.getElementById('favorecido').value = '';

    carregarMovimentacoes();

} else {

    alert(data.erro || 'Erro na transferência');

}

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
    const transferencia = document.getElementById('valor-transferencia');

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
                    <td style="color: orange;">${s.status}</td>
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

    if (transferencia) {
        transferencia.value = Number(data.ganhos || 0)
        .toFixed(2)
        .replace(".", ",");
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

// ========================
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
