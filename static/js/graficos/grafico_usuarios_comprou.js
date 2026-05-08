fetch('/api/usuarios-data')
    .then(response => response.json())
    .then(usuariosData => {
        const canvasUsuarios = document.getElementById('usuariosChart');
        const ctx_usuarios = canvasUsuarios.getContext('2d');
        
        
        const labelsV = Object.keys(usuariosData);
        const valoresV = labelsV.map(v => usuariosData[v].approved);

        new Chart(ctx_usuarios, {
            type: 'polarArea',
            data: {
                labels: labelsV,
                datasets: [{
                    label: 'Compras (R$)',
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
                    title: { display: true, text: 'Compras usuarios' }
                }
            }
        });
    });
