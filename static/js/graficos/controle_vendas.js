// async function buscarDados() {
//   const cpf = document.getElementById("dados-filter").value;

//   try {
//     const response = await fetch(`/api/clientes?cpf=${cpf}`);
//     const dados = await response.json();

//     const tabela = document.getElementById("tabela-clientes");
//     tabela.innerHTML = "";

//     if (!dados || dados.length === 0) {
//       tabela.innerHTML = `<tr><td colspan="8">Nenhum cliente encontrado</td></tr>`;
//       return;
//     }

//     dados.forEach(cliente => {
//       tabela.innerHTML += `
//         <tr>
//           <td>${cliente.imagem_bilhete || ""}</td>
//           <td>${cliente.numero || ""}</td>
//           <td>${cliente.nome || ""}</td>
//           <td>${cliente.sobrenome || ""}</td>
//           <td>${cliente.cpf || ""}</td>
//           <td>${cliente.email || ""}</td>
//           <td>${cliente.vendedor || ""}</td>
//         </tr>
//       `;
//     });

//   } catch (err) {
//     alert("Erro ao buscar dados");
//   }
// }

let acaoAtual = null;
let linhaAtual = null;

function abrirModal(acao, btn) {
    acaoAtual = acao;
    linhaAtual = btn.closest("tr");
    document.getElementById("modalSenha").style.display = "flex";
}

function fecharModal() {
    document.getElementById("modalSenha").style.display = "none";
    document.getElementById("senhaInput").value = "";
}

function confirmarAcao() {
    const senha = document.getElementById("senhaInput").value;

    // SEM FUNÇÃO DE VALIDAÇÃO (como você pediu)
    console.log("Senha digitada:", senha);
    console.log("Ação:", acaoAtual);

    fecharModal();
}