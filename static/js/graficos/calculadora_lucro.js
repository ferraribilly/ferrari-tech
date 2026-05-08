function v(id){
  let x = document.getElementById(id).innerText.trim();
  return x === "" ? 0 : x.replace(",", ".");
}

function calcular(){
  fetch("/calcular-rifa", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      nome: "Rifa",
      investimento: v("investimento"),
      despesas: v("despesas"),
      aliquota_imposto: v("aliquota_imposto"),
      taxa_mp: v("taxa_mp"),
      qtd: v("qtd"),
      valor: v("valor"),
      data_sorteio: document.getElementById("data_sorteio").value,
      hora_sorteio: document.getElementById("hora_sorteio").value
    })
  })
  .then(r=>r.json())
  .then(r=>{
    document.getElementById("resultado").innerHTML = r.tabela_html;
  });
}