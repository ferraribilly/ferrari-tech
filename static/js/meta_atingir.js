let projetoAtual = null;

async function carregarProjeto() {
    const res = await fetch("/listar_projetos");
    const data = await res.json();

    // pega o primeiro projeto (ou ajuste filtro depois se quiser)
    projetoAtual = data.projetos[0];

    atualizarTempo();
}




function atualizarTempo(vendidos = 0) {
    if (!projetoAtual) return;

    // META vem da collection
    const meta = Number(projetoAtual.quantidade);
    
    

    

    // PRAZO vem da collection
    const prazo = new Date(projetoAtual.dt_sorteio + "T23:59:59");

    const hoje = new Date();
    const diff = prazo - hoje;

    const diasRestantes = Math.max(
        Math.floor((prazo.getTime() - hoje.getTime()) / (1000 * 60 * 60 * 24)),
        0
    );

    const totalDias = Math.max(
        Math.ceil((prazo - hoje) / (1000 * 60 * 60 * 24)) + diasRestantes,
        1
    );

    const porcentagemDias = Math.min(((totalDias - diasRestantes) / totalDias) * 100, 100);

    const timeChart = document.getElementById("timeChart");
    if (timeChart) {
        timeChart.style.background = `conic-gradient(#f39c12 0% ${porcentagemDias}%, #ddd ${porcentagemDias}% 100%)`;
        timeChart.textContent = diasRestantes + " dias";
    }

    const restante = Math.max(meta - vendidos, 0);
    const media = diasRestantes > 0 ? Math.ceil(restante / diasRestantes) : restante;

    const mediaEl = document.getElementById("mediaDiaria");
    if (mediaEl) {
        mediaEl.textContent = "📌 Média diária necessária: " + media + " números/dia";
    }
}

carregarProjeto();
setInterval(atualizarTempo, 1000 * 60 * 60);


