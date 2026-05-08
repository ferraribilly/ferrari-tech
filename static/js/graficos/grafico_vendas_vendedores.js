const canvasVendedores = document.getElementById('vendedoresChart');

const ctx_vendedores = canvasVendedores.getContext('2d');

const labelsV = Object.keys(vendedoresData);
const valoresV = labelsV.map(v => vendedoresData[v].approved);

new Chart(ctx_vendedores, {
    type: 'polarArea',
    data: {
        labels: labelsV,
        datasets: [{
            label: 'Vendas (R$)',
            data: valoresV,
            backgroundColor: [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'top' },
            title: {
                display: true,
                text: 'Vendas por Vendedor'
            }
        }
    }
});


        const vendedores = ['Carlos', '', '', ''];
        const aprovados = [0.25, 0, 0, 0]; // Venda Aprovada (Entrada)
        const cancelados = [0.30, 0, 0, 0];   // Venda Cancelada (Saída)
        const comissaoPercentual = 0.30;

        // Cálculo da Comissão (30% sobre aprovados)
        const comissoes = aprovados.map(valor => valor * comissaoPercentual);

        const ctx_finance = document.getElementById('financeChart').getContext('2d');
        const vendasChart = new Chart(ctx_finance, {
            type: 'bar', // Tipo barra
            data: {
                labels: vendedores,
                datasets: [
                    {
                        label: 'Vendas Aprovadas (Entrada)',
                        data: aprovados,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)', // Azul
                        stack: 'vendas',
                    },
                    {
                        label: 'Vendas Canceladas (Saída)',
                        data: cancelados.map(v => -v), // Valores negativos para visualização de saída
                        backgroundColor: 'rgba(255, 99, 132, 0.7)', // Vermelho
                        stack: 'vendas',
                    },
                    {
                        label: 'Comissão 30% (Aprovado)',
                        data: comissoes,
                        backgroundColor: 'rgba(75, 192, 192, 0.8)', // Verde
                        stack: 'comissao',
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: { stacked: true }, // Empilhar no eixo X
                    y: { 
                        stacked: true, // Empilhar no eixo Y
                        beginAtZero: true,
                        title: { display: true, text: 'Valor (R$)' }
                    }
                },
                plugins: {
                    title: { display: true, text: 'Extrato: Entrada, Saída e Comissão Vendedores' },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Math.abs(context.parsed.y));
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });