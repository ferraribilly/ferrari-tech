const ctx = document.getElementById('faturamentoChart').getContext('2d');

const faturamentoChart = new Chart(ctx, {
    type: 'bar', // Tipo do gráfico
    data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        datasets: [{
            label: 'Faturamento (R$)',
            data: [12000, 19000, 3000, 5000, 23000, 15000],
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
