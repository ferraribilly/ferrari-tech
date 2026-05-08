const ctx_faturamento = document.getElementById('faturamentoChart').getContext('2d');

const ordemMeses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];
const labels = ordemMeses;

// usa o objeto certo vindo do backend
const valores = ordemMeses.map(m => resumo.faturamento_mensal[m] || 0);

new Chart(ctx_faturamento, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: 'Faturamento (R$)',
            data: valores,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return 'R$ ' + value.toFixed(2);
                    }
                }
            }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return 'R$ ' + context.raw.toFixed(2);
                    }
                }
            }
        }
    }
});