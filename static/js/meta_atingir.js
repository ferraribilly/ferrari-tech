    
    const prazo = new Date("2026-05-10T23:59:59");


    function atualizarTempo(vendidos=0) {
      const meta = 1000;
      const hoje = new Date();
      const diff = prazo - hoje;
      const diasRestantes = Math.max(Math.ceil(diff / (1000 * 60 * 60 * 24)), 0);

      // Total de dias entre hoje e prazo
      const totalDias = Math.ceil((prazo - new Date("2026-03-22T00:00:00")) / (1000 * 60 * 60 * 24));
      const porcentagemDias = Math.min(((totalDias - diasRestantes) / totalDias) * 100, 100);

      const timeChart = document.getElementById("timeChart");
      timeChart.style.background = `conic-gradient(#f39c12 0% ${porcentagemDias}%, #ddd ${porcentagemDias}% 100%)`;
      timeChart.textContent = diasRestantes + " dias";

      // Cálculo da média diária necessária
      const restante = Math.max(meta - vendidos, 0);
      const media = diasRestantes > 0 ? Math.ceil(restante / diasRestantes) : restante;
      document.getElementById("mediaDiaria").textContent = "📌 Média diária necessária: " + media + " números/dia";
    }

    // Atualiza automaticamente o gráfico de tempo
    atualizarTempo();
    setInterval(atualizarTempo, 1000 * 60 * 60); // atualiza a cada hora