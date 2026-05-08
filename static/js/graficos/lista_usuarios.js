async function buscarDados() {
  const cpf = document.getElementById("dados-filter").value;

  if (!cpf) {
    alert("Informe o CPF");
    return;
  }

  try {
    const response = await fetch(`/api/clientes?cpf=${cpf}`);
    const dados = await response.json();

    const tabela = document.getElementById("tabela-clientes");
    tabela.innerHTML = "";

    if (!dados || dados.length === 0) {
      tabela.innerHTML = `<tr><td colspan="9">Nenhum cliente encontrado</td></tr>`;
      return;
    }

    dados.forEach(cliente => {
      tabela.innerHTML += `
        <tr>
          <td>${cliente.id || ""}</td>
          <td>${cliente.nome || ""}</td>
          <td>${cliente.sobrenome || ""}</td>
          <td>${cliente.dt_nascimento || ""}</td>
          <td>${cliente.cpf || ""}</td>
          <td>${cliente.email || ""}</td>
          <td>${cliente.estado || ""}</td>
          <td>${cliente.chavePix || ""}</td>
          <td>${cliente.vendedor || ""}</td>
        </tr>
      `;
    });

  } catch (err) {
    alert("Erro ao buscar dados");
  }
}