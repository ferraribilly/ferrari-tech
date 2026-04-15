let quantidade = 0;
let valorUnitario = 0.05;
let numerosSelecionados = [];

async function gerarBilhete() {

    const input = document.querySelector('.input-numero');
    const numero = input.value || '0000';

    quantidade++;
    numerosSelecionados.push(numero);

    const total = quantidade * valorUnitario;
    document.getElementById("total").innerText = total.toFixed(2);

    const usuario_id = document.getElementById("usuario_id").innerText;
    const nome = document.getElementById("nome").innerText;
    const cpf = document.getElementById("cpf").innerText;
    const email = document.getElementById("email").innerText;

    const paymentId = document.getElementById("payment_id")?.innerText || "aguardando";
    const valor = document.getElementById("valor")?.innerText || "0.05";
    const dataSort = document.getElementById("dataSort")?.innerText || "10/05/2026";


    // GERA IMAGEM
    const res = await fetch("/gerar-bilhete", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            numero,
            nome,
            email,
            cpf
        })
    });

    const data = await res.json();




    

    const container = document.getElementById("cards");

    const card = document.createElement("div");
    card.style.background = "#111";
    card.style.padding = "10px";
    card.style.borderRadius = "10px";
    card.style.marginTop = "10px";

    const img = document.createElement("img");
    img.src = data.img + "?t=" + new Date().getTime();
    img.style.width = "100%";
    img.style.borderRadius = "8px";

    card.appendChild(img);
    container.prepend(card);

    input.value = '';


const lista = document.getElementById("lista-numeros");

// limpa antes de renderizar
lista.innerHTML = "";

// adiciona todos os números gerados
numerosSelecionados.forEach(num => {
    const item = document.createElement("div");
    item.innerText = num;
    item.style.color = "#f1eeee";
    item.style.fontWeight = "bold";
    lista.appendChild(item);
});
}


  const modal = document.getElementById('modal');
  const confirmBtn = document.getElementById('confirmBtn');
 

  confirmBtn.addEventListener('click', () => modal.style.display = 'flex');
  cancelBtn.addEventListener('click', () => modal.style.display = 'none');
  
  // Fecha modal ao clicar fora
  window.addEventListener('click', (e) => {
    if (e.target === modal) modal.style.display = 'none';
  });



