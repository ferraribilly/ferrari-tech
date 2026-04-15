const ctx_mais_vendidos = document.getElementById('myDoughnutChart').getContext('2d');

const myDoughnutChart = new Chart(ctx_mais_vendidos, {
    type: 'doughnut',
    data: {
        labels: ['Pix no Bolso', 'Quarta Premiada', 'Bilhete Ganhador', 'Acessórios'],
        datasets: [{
            label: 'Vendas',
            data: [45, 30, 15, 10], // Valores em porcentagem ou quantidade
            backgroundColor: [
                '#FF6384', // Rosa
                '#36A2EB', // Azul
                '#FFCE56', // Amarelo
                '#4BC0C0'  // Verde
            ],
            hoverOffset: 10 // Efeito ao passar o mouse
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom', // Posição da legenda
            },
            title: {
                display: true,
                text: 'Top Vendas 2024'
            }
        },
        cutout: '70%' // Define o tamanho do "buraco" da rosca
    }
});

    