 // Faturamento por Canal
new Chart(document.getElementById('projetos'), {
  type: 'pie',
  data: {
    labels: ['Store','Online','Reseller','Catalog'],
    datasets: [{
      data: [54.33,22.87,14.57,8.24],
      backgroundColor: ['#27ae60','#2980b9','#f39c12','#8e44ad']
    }]
  },
  options: {
    maintainAspectRatio: false
  }
});  




    