const ctx_impostos = document.getElementById('impostosChart').getContext('2d');
const impostosChart = new Chart(ctx_impostos, {
    type: 'polarArea', // Tipo do gráfico
    data: {
        labels: ['IRPF', 'IPTU', 'IPVA', 'ISS', 'ICMS'],
        datasets: [{
            label: 'Valor a Pagar (R$)',
            data: [2500, 1200, 1800, 500, 3000],
            backgroundColor: [
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(153, 102, 255, 0.7)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'right',
            }
        }
    }
});