const ctx1 = document.getElementById('despesasChart').getContext('2d');

// Dados simulados de despesas
const data = {
    labels: ['Jan', 'Fev', 'Mar', 'Abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'], // Eixo X: Data/Mês
    datasets: [{
        label: 'Despesas (R$)',
        data: [1200, 1500, 900, 2100, 0, 0, 0, 0, 0, 0, 0, 0], // Eixo Y: Valores
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.3, // Suavidade da linha
        fill: true,
        pointBackgroundColor: 'rgb(75, 192, 192)',
        pointRadius: 5
    }]
};

// Configurações do gráfico
const config = {
    type: 'line',
    data: data,
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
};

// Renderizar o gráfico
const despesasChart = new Chart(ctx1, config);
