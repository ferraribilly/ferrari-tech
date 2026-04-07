let quantidade = 0;
let valorUnitario = 0.05;



let numerosSelecionados = [];

function gerarBilhete() {
  const input = document.querySelector('.input-numero');
  const numero = input.value || '000';

  const cards = document.getElementById('cards');

  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `
    <div class="card-content">
      <h3 style="color:#fff; font-family:monospace; border:1px solid #fff; border-radius: 3px; background: #555;">
        NUMERO:<span style="color:blue; background: #fff; border-radius:5px;">${numero}</span>
      </h3>
    </div>
  `;

  cards.appendChild(card);

  quantidade++;
  numerosSelecionados.push(numero);

  const total = quantidade * valorUnitario;
  document.getElementById("total").innerText = total.toFixed(2);

  const usuario_id = document.getElementById("usuario_id").innerText;
  const nome = document.getElementById("nome").innerText;
  const cpf = document.getElementById("cpf").innerText;
  const email = document.getElementById("email").innerText;
  const paymentId = document.getElementById("payment_id")?.innerText || "aguardando gerar payment_id Mercado Pago";
  const valor = document.getElementById("valor")?.innerText || "1.00";
  const dataSort = document.getElementById("dataSort")?.innerText || "10/05/2026";

  fetch("/numeros", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      usuario_id: usuario_id,
      nome: nome,
      cpf: cpf,
      email: email,
      numero: numero,
      paymentId: paymentId,
      valor: parseFloat(valor),
      dataSort: dataSort
    })
  })
  .then(res => res.json())
  .then(data => {
    console.log("Salvo:", data);
  })
  .catch(err => {
    console.error("Erro ao salvar:", err);
  });

  input.value = '';
}


//DELETAR NUMEROS
function deletarNumero(id) {
  fetch(`/numeros/${id}`, {
    method: "DELETE"
  })
  .then(res => res.json())
  .then(data => {
    console.log(data);
  })
  .catch(err => console.error(err));
}


// // Carregar lista de números 
async function carregarNumeros() {
    const res = await fetch("/numeros");
    const data = await res.json();
    const lista = document.getElementById("listaNumeros");
    lista.innerHTML = "";
    data.forEach(item => {
        const li = document.createElement("li");
        li.className = "list-group-item";
        li.textContent = `Número: ${String(item.numero).padStart(3, '0')} - Valor: R$ ${item.valor.toFixed(2)} - Comprovante: ${item.url_comprovante}`;
        lista.appendChild(li);
    });
}