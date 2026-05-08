// Dados vindos do Flask
  

  // Ordem fixa dos meses
  const ordemMeses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];

  // Extrai valores na ordem correta
  const valoresMeses = ordemMeses.map(m => faturamentoMensal[m] || 0);

  // Cria o gráfico de faturamento por mês
  new Chart(document.getElementById('faturamentoMes'), {
    type: 'bar',
    data: {
      labels: ordemMeses,
      datasets: [{
        label: 'Faturamento (R$)',
        data: valoresMeses,
        backgroundColor: '#27ae60'
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Faturamento (R$)' }
        }
      },
      plugins: {
        title: {
          display: true,
          text: 'Faturamento por Mês'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              let valor = context.parsed.y;
              return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
            }
          }
        }
      }
    }
  });


  // cálculo da margem
  const resumo = { numeros_aprovados: 6 }; 
  const meta = 300; 
  const porcentagem = Math.round((resumo.numeros_aprovados / meta) * 100);

  // Atualiza o card de métricas
  document.getElementById("margemValor").innerText = porcentagem + "%";

  // Cria o gráfico de linha
  new Chart(document.getElementById('margemMes'), {
    type: 'line',
    data: {
      labels: ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'],
      datasets: [{
        label: 'Margem (%)',
        data: [0,0,0,porcentagem,0,0,0,0,0,0,0,0], // coloca o valor calculado em Abril
        borderColor: '#2980b9',
        backgroundColor: 'rgba(41, 128, 185, 0.2)',
        fill: true,
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          title: { display: true, text: 'Margem (%)' }
        }
      }
    }
  });




// Extrai nomes e apenas valores approved
  const nomesVendedores = Object.keys(vendedoresData);
  const valoresApproved = nomesVendedores.map(v => vendedoresData[v].approved);

  // Cria o gráfico somente com approved
  new Chart(document.getElementById('faturamentoLoja'), {
    type: 'bar',
    data: {
      labels: nomesVendedores,
      datasets: [{
        label: 'Faturamento Aprovado (R$)',
        data: valoresApproved,
        backgroundColor: '#e67e22'
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Faturamento (R$)' }
        }
      },
      plugins: {
        title: {
          display: true,
          text: 'Faturamento por Vendedores (Approved)'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              let valor = context.parsed.y;
              return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
            }
          }
        }
      }
    }
  });

  // 
 new Chart(document.getElementById('faturamentoCategoria'), {
  type: 'bar',
  data: {
    labels: Object.keys(vendedoresData),
    datasets: [{
      label: 'Quantidade numeros vendidos (R$)',
      data: Object.values(vendedoresData).map(v => v.numeros),
      backgroundColor: '#9b59b6'
    }]
  }
});