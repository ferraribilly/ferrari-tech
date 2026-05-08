async function buscarDados() {
  const cpf = document.getElementById("dados-filter").value;

  try {
    const response = await fetch(`/api/vendedores?cpf=${cpf}`);
    const dados = await response.json();

    const tabela = document.getElementById("tabela-vendedores");
    tabela.innerHTML = "";

    if (!dados || dados.length === 0) {
      tabela.innerHTML = `<tr><td colspan="8">Nenhum vendedor encontrado</td></tr>`;
      return;
    }

    dados.forEach(vendedor => {
      tabela.innerHTML += `
        <tr>
          <td>${vendedor.id || ""}</td>
          <td>${vendedor.nome || ""}</td>
          <td>${vendedor.sobrenome || ""}</td>
          <td>${vendedor.dt_nascimento || ""}</td>
          <td>${vendedor.cpf || ""}</td>
          <td>${vendedor.email || ""}</td>
          <td>${vendedor.chavePix || ""}</td>
        </tr>
      `;
    });

  } catch (err) {
    alert("Erro ao buscar dados");
  }
}



