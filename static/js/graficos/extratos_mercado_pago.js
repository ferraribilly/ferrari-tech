fetch("/支付列表")
.then(res => res.json())
.then(data => {

    const tbody = document.getElementById("extrato-body");
    tbody.innerHTML = "";

    let totalAprovado = 0;
    let totalCancelado = 0;
    let totalPendente = 0;
    let totalTaxa = 0;
    let totalSaques = 0;

    data.pagamentos.forEach(p => {

        const valorNum = Number(p.valor || 0);
        const taxaNum = Number(p.taxa_mp || 0); // 🔥 PEGA TAXA DO BACKEND

        const dataObj = new Date(p.data_criacao);
        const dataFormatada = dataObj.toLocaleDateString("pt-BR");

        const horaFormatada = dataObj.toLocaleTimeString("pt-BR", {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });

        const descricao = "Números: " + (p.lista_numeros ? p.lista_numeros.join(", ") : "-");

        const valor = valorNum.toFixed(2).replace(".", ",");
        const taxaFormatada = taxaNum.toFixed(2).replace(".", ",");

        let valorClass = "";
        let sinal = "";
        let statusClass = "";
        let statusTexto = "";

        if (p.status === "approved") {

            valorClass = "valor-positivo";
            sinal = "+";
            statusClass = "status-pago";
            statusTexto = "Pago";

            totalAprovado += valorNum;
            totalTaxa += taxaNum;

        } else if (p.status === "pending") {

            valorClass = "valor-negativo";
            sinal = "-";
            statusClass = "status-pendente";
            statusTexto = "Pendente";

            totalPendente += valorNum;

        } else {

            valorClass = "valor-negativo";
            sinal = "-";
            statusClass = "status-cancelado";
            statusTexto = "Cancelado";

            totalCancelado += valorNum;
        }

        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${p._id || "-"}</td>
            <td>${dataFormatada}</td>
            <td>${horaFormatada}</td>
            <td>${descricao}</td>
            <td class="${valorClass}">${sinal} R$ ${valor}</td>
            <td>R$ ${taxaFormatada}</td> <!-- 🔥 TAXA NA TABELA -->
            <td><span class="status ${statusClass}">${statusTexto}</span></td>
        `;

        tbody.appendChild(tr);
    });

    data.saques.forEach(s => {

        const valorNum = Number(s.valor_saque || 0);
        totalSaques += valorNum;

        const dataObj = new Date(s.criado_em);
        const dataFormatada = dataObj.toLocaleDateString("pt-BR");
        const horaFormatada = dataObj.toLocaleTimeString("pt-BR");

        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${s.identificacao}</td>
            <td>${dataFormatada}</td>
            <td>${horaFormatada}</td>
            <td>${s.descricao}</td>
            <td class="valor-negativo">- R$ ${valorNum.toFixed(2).replace(".", ",")}</td>
            <td>-</td>
            <td><span class="status status-cancelado">Saque</span></td>
        `;

        tbody.appendChild(tr);
    });

    const formatar = v => "R$ " + v.toFixed(2).replace(".", ",");

    document.getElementById("total-aprovado").innerText = formatar(totalAprovado);
    document.getElementById("total-cancelado").innerText = formatar(totalCancelado);
    document.getElementById("total-pendente").innerText = formatar(totalPendente);
    document.getElementById("taxa-mp").innerText = formatar(totalTaxa);
    document.getElementById("total-saques").innerText = formatar(totalSaques);

    const saldoAtual = totalAprovado - totalTaxa - totalSaques;
    document.getElementById("saldo-atual").innerText = formatar(saldoAtual);

})
.catch(err => console.error("Erro:", err));fetch("/支付列表")
.then(res => res.json())
.then(data => {

    const tbody = document.getElementById("extrato-body");
    tbody.innerHTML = "";

    let totalAprovado = 0;
    let totalCancelado = 0;
    let totalPendente = 0;
    let totalTaxa = 0;
    let totalSaques = 0;

    data.pagamentos.forEach(p => {

        const valorNum = Number(p.valor || 0);
        const taxaNum = Number(p.taxa_mp || 0);

        const dataObj = new Date(p.data_criacao);
        const dataFormatada = dataObj.toLocaleDateString("pt-BR");

        const horaFormatada = dataObj.toLocaleTimeString("pt-BR", {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });

        const descricao = "Números: " + (p.lista_numeros ? p.lista_numeros.join(", ") : "-");

        const valor = valorNum.toFixed(2).replace(".", ",");

        let valorClass = "";
        let sinal = "";
        let statusClass = "";
        let statusTexto = "";

        if (p.status === "approved") {

            valorClass = "valor-positivo";
            sinal = "+";
            statusClass = "status-pago";
            statusTexto = "Pago";

            totalAprovado += valorNum;
            totalTaxa += taxaNum;

        } else if (p.status === "pending") {

            valorClass = "valor-negativo";
            sinal = "-";
            statusClass = "status-pendente";
            statusTexto = "Pendente";

            totalPendente += valorNum;

        } else {

            valorClass = "valor-negativo";
            sinal = "-";
            statusClass = "status-cancelado";
            statusTexto = "Cancelado";

            totalCancelado += valorNum;
        }

        // 🔥 LINHA DO PAGAMENTO
        const trPagamento = document.createElement("tr");

        trPagamento.innerHTML = `
            <td>${p._id || "-"}</td>
            <td>${dataFormatada}</td>
            <td>${horaFormatada}</td>
            <td>${descricao}</td>
            <td class="${valorClass}">${sinal} R$ ${valor}</td>
            <td><span class="status ${statusClass}">${statusTexto}</span></td>
        `;

        tbody.appendChild(trPagamento);

        // 🔥 LINHA DA TAXA (SEPARADA)
        if (p.status === "approved" && taxaNum > 0) {

            const trTaxa = document.createElement("tr");

            trTaxa.innerHTML = `
                <td>${p._id}</td>
                <td>${dataFormatada}</td>
                <td>${horaFormatada}</td>
                <td>Taxa Mercado Pago</td>
                <td class="valor-negativo">- R$ ${taxaNum.toFixed(2).replace(".", ",")}</td>
                <td><span class="status status-cancelado">Taxa</span></td>
            `;

            tbody.appendChild(trTaxa);
        }

    });

    data.saques.forEach(s => {

        const valorNum = Number(s.valor_saque || 0);
        totalSaques += valorNum;

        const dataObj = new Date(s.criado_em);
        const dataFormatada = dataObj.toLocaleDateString("pt-BR");
        const horaFormatada = dataObj.toLocaleTimeString("pt-BR");

        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${s.identificacao}</td>
            <td>${dataFormatada}</td>
            <td>${horaFormatada}</td>
            <td>${s.descricao}</td>
            <td class="valor-negativo">- R$ ${valorNum.toFixed(2).replace(".", ",")}</td>
            <td><span class="status status-cancelado">Saque</span></td>
        `;

        tbody.appendChild(tr);
    });

    const formatar = v => "R$ " + v.toFixed(2).replace(".", ",");

    document.getElementById("total-aprovado").innerText = formatar(totalAprovado);
    document.getElementById("total-cancelado").innerText = formatar(totalCancelado);
    document.getElementById("total-pendente").innerText = formatar(totalPendente);
    document.getElementById("taxa-mp").innerText = formatar(totalTaxa);
    document.getElementById("total-saques").innerText = formatar(totalSaques);

    const saldoAtual = totalAprovado - totalTaxa - totalSaques;
    document.getElementById("saldo-atual").innerText = formatar(saldoAtual);

})
.catch(err => console.error("Erro:", err));