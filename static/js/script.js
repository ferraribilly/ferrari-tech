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

// Carregar lista de números 
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


// PAGAMENTO QRCODE PIX
document.getElementById("btn-pagar").onclick = () => {

    const nome = document.getElementById("nome").innerText;
    const cpf = document.getElementById("cpf").innerText;
    const email = document.getElementById("email").innerText;

    const url = `/payment_qrcode_pix/pagamento_pix/{{ usuario_id }}`
        + `?nome=${encodeURIComponent(nome)}`
        + `&cpf=${encodeURIComponent(cpf)}`
        + `&email=${encodeURIComponent(email)}`
        + `&quantidade=${quantidade}`;

    window.location.href = url;
};

// PAGAMENTO PREFERENCE MERCADO PAGO
document.getElementById("btn-preference").onclick = () => {

    const nome = document.getElementById("nome").innerText;
    const cpf = document.getElementById("cpf").innerText;
    const email = document.getElementById("email").innerText;

    const url = `/compra/preference/pagamento_pix/{{ usuario_id }}`
        + `?nome=${encodeURIComponent(nome)}`
        + `&cpf=${encodeURIComponent(cpf)}`
        + `&email=${encodeURIComponent(email)}`
        + `&quantidade=${quantidade}`;

    window.location.href = url;
};


var usuario_Id = "{{ usuario_id }}";



document.getElementById('copy').addEventListener('click', copyText);
document.getElementById('copy-mobile').addEventListener('click', copyText);

function copyText() {
    var qrcodeText = document.getElementById('qrcode-text');
    var copiedCodeBox = document.getElementById('copied-code');

    navigator.clipboard.writeText(qrcodeText.textContent).then(function () {
        // Efeito de blur e mostrar mensagem
        qrcodeText.style.filter = 'blur(1px)';
        copiedCodeBox.style.visibility = 'visible';
        copiedCodeBox.style.opacity = '0.9';
        copiedCodeBox.style.transition = 'all 0.3s';

        setTimeout(function () {
            qrcodeText.style.filter = '';
            copiedCodeBox.style.visibility = '';
            copiedCodeBox.style.opacity = '';
        }, 5000);

        // Redirecionar após copiar
        var id = qrcodeText.dataset.id; // Se você tiver o ID armazenado no data-id
        window.location.href = '/pendente/{{ usuario_id }}'
    });
}

var paymentId = "{{ payment_id }}";
var usuario_Id = "{{ usuario_id }}";
var socket = io(window.location.origin);

socket.on("connect", function () {
    socket.emit("join_payment", { payment_id: paymentId });
});

socket.on("payment_update", function (data) {
    if (data.payment_id !== paymentId) return;

    var div = document.getElementById("notifications");
    var p = document.createElement("p");

    if (data.status === "approved") {
        p.style.color = "green";
        p.innerText = "✅ Pagamento aprovado com sucesso!";
        div.innerHTML = "";
        div.appendChild(p);

        setTimeout(function () {
            
            window.location.href = `/aprovado?id=${usuario_Id}`;
        }, 3000);

    } else {
        p.style.color = "red";
        p.innerText = "❌ Pagamento recusado!";
        div.innerHTML = "";
        div.appendChild(p);

        setTimeout(function () {
            window.location.href = `/recusado?id=${usuario_Id}`;
        }, 3000);
    }
});

class Accordion {
  constructor(accordionListQuestions) {
    this.accordionListQuestions = document.querySelectorAll(accordionListQuestions);
    this.activeItemClass = "active";
  }

  toggleAccordion(item) {
    item.classList.toggle(this.activeItemClass);
    item.nextElementSibling.classList.toggle(this.activeItemClass);
  }

  addAccordionEvent() {
    this.accordionListQuestions.forEach((question) => {
      question.addEventListener("click", () => this.toggleAccordion(question));
    });
  }

  init() {
    if (this.accordionListQuestions.length) {
      this.addAccordionEvent();
    }
    return this;
  }
}

const accordion = new Accordion(".faq-question");
accordion.init();

fetch("/registro_participantes")
.then(res => res.text())
.then(html => {
    document.getElementById("areaAuth").innerHTML = html;
});

function mostrarLogin() {
    document.getElementById("loginBox").style.display = "block";
    document.getElementById("registroBox").style.display = "none";

    document.getElementById("btnLogin").classList.add("active");
    document.getElementById("btnRegistro").classList.remove("active");
}

function mostrarRegistro() {
    document.getElementById("loginBox").style.display = "none";
    document.getElementById("registroBox").style.display = "block";

    document.getElementById("btnRegistro").classList.add("active");
    document.getElementById("btnLogin").classList.remove("active");
}