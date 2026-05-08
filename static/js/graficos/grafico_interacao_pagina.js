const ctx = document.getElementById('curtidasPagina').getContext('2d');

const myChart = new Chart(ctx, {
    type: 'bar', // Tipo de gráfico: barras
    data: {
        // Nomes dos usuários
        labels: ['Ana', 'Bruno', 'Carla', 'Diego'],
        datasets: [
            {
                label: 'Gostei 👍',
                data: [12, 19, 3, 5], // Valores para gostei
                backgroundColor: 'rgba(54, 162, 235, 0.6)', // Azul
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            },
            {
                label: 'Não Gostei 👎',
                data: [2, 5, 8, 3], // Valores para não gostei
                backgroundColor: 'rgba(255, 99, 132, 0.6)', // Vermelho
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }
        ]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true // Garante que o eixo y comece no 0
            }
        }
    }
});
