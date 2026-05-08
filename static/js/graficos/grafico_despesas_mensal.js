const ctx1 = document.getElementById('resumoFerrariTech').getContext('2d');

const data = {
    labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],

    datasets: [

        {
            label: 'MONGODB (R$ 285)',
            data: [0, 0, 0, 285, 0, 0, 0, 0, 0, 0, 0, 0],
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            tension: 0.3,
            fill: true,
            pointRadius: 5
        },

        {
            label: 'CLOUDINARY (R$ 145)',
            data: [0, 0, 0, 145, 0, 0, 0, 0, 0, 0, 0, 0],
            borderColor: 'rgb(54, 162, 235)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            tension: 0.3,
            fill: true,
            pointRadius: 5
        },

        // {
        //     label: 'TAXA MP 0.99%',
        //     data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        //     borderColor: 'rgb(75, 192, 192)',
        //     backgroundColor: 'rgba(75, 192, 192, 0.2)',
        //     tension: 0.3,
        //     fill: true
        // },

        // {
        //     label: 'VENDEDORES 30%',
        //     data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        //     borderColor: 'rgb(153, 102, 255)',
        //     backgroundColor: 'rgba(153, 102, 255, 0.2)',
        //     tension: 0.3,
        //     fill: true
        // },

        {
            label: 'RENDER',
            data: [0, 0, 0, 35, 0, 0, 0, 0, 0, 0, 0, 0],
            borderColor: 'rgb(255, 206, 86)',
            backgroundColor: 'rgba(255, 206, 86, 0.2)',
            tension: 0.3,
            fill: true
        },



        // {
        //     label: 'IBS/CBS',
        //     data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        //     borderColor: 'rgb(255, 87, 34)',
        //     backgroundColor: 'rgba(255, 87, 34, 0.2)',
        //     tension: 0.3,
        //     fill: true
        // },

        // // 🔥 NOVO: INVESTIMENTO PREMIAÇÃO
        // {
        //     label: 'INVESTIMENTO PREMIAÇÃO',
        //     data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        //     borderColor: 'rgb(233, 30, 99)',
        //     backgroundColor: 'rgba(233, 30, 99, 0.2)',
        //     tension: 0.3,
        //     fill: true,
        //     pointRadius: 5
        // }

    ]
};

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

const despesasChart = new Chart(ctx1, config);