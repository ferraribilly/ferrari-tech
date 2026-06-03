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

    // 🔥 FUNÇÃO PRA ARRUMAR DATA
    function formatarData(dataString) {

        if (!dataString) {
            return {
                data: "-",
                hora: "-"
            };
        }

        try {

            // 🔥 EXEMPLO:
            // Wed, 20 de May de 2026 21:26:45 GMT

            const limpa = dataString
                .replace(/ de /g, " ")
                .replace("GMT", "")
                .trim();

            const dataObj = new Date(limpa);

            if (isNaN(dataObj.getTime())) {

                return {
                    data: "-",
                    hora: "-"
                };
            }

            return {
                data: dataObj.toLocaleDateString("pt-BR"),
                hora: dataObj.toLocaleTimeString("pt-BR", {
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit"
                })
            };

        } catch (e) {

            return {
                data: "-",
                hora: "-"
            };
        }
    }

    data.pagamentos.forEach(p => {

        const valorNum = Number(p.valor || 0);
        const taxaNum = Number(p.taxa_mp || 0);

        const dataInfo = formatarData(p.data_criacao);

        const descricao = "Números: " + (
            p.lista_numeros
                ? p.lista_numeros.join(", ")
                : "-"
        );

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

        // 🔥 LINHA PAGAMENTO
        const trPagamento = document.createElement("tr");

        trPagamento.innerHTML = `
            <td>${p._id || "-"}</td>
            <td>${dataInfo.data}</td>
            <td>${dataInfo.hora}</td>
            <td>${descricao}</td>
            <td class="${valorClass}">${sinal} R$ ${valor}</td>
            <td><span class="status ${statusClass}">${statusTexto}</span></td>
        `;

        tbody.appendChild(trPagamento);

        // 🔥 LINHA TAXA
        if (p.status === "approved" && taxaNum > 0) {

            const trTaxa = document.createElement("tr");

            trTaxa.innerHTML = `
                <td>${p._id}</td>
                <td>${dataInfo.data}</td>
                <td>${dataInfo.hora}</td>
                <td>Taxa Mercado Pago</td>
                <td class="valor-negativo">
                    - R$ ${taxaNum.toFixed(2).replace(".", ",")}
                </td>
                <td>
                    <span class="status status-cancelado">Taxa</span>
                </td>
            `;

            tbody.appendChild(trTaxa);
        }

    });

    data.saques.forEach(s => {

        const valorNum = Number(s.valor_saque || 0);

        totalSaques += valorNum;

        const dataInfo = formatarData(s.criado_em);

        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${s.identificacao}</td>
            <td>${dataInfo.data}</td>
            <td>${dataInfo.hora}</td>
            <td>${s.descricao}</td>
            <td class="valor-negativo">
                - R$ ${valorNum.toFixed(2).replace(".", ",")}
            </td>
            <td>
                <span class="status status-cancelado">Saque</span>
            </td>
        `;

        tbody.appendChild(tr);

    });

    const formatar = v =>
        "R$ " + v.toFixed(2).replace(".", ",");

    document.getElementById("total-aprovado").innerText =
        formatar(totalAprovado);

    document.getElementById("total-cancelado").innerText =
        formatar(totalCancelado);

    document.getElementById("total-pendente").innerText =
        formatar(totalPendente);

    document.getElementById("taxa-mp").innerText =
        formatar(totalTaxa);

    document.getElementById("total-saques").innerText =
        formatar(totalSaques);

    const saldoAtual =
        totalAprovado - totalTaxa - totalSaques;

    document.getElementById("saldo-atual").innerText =
        formatar(saldoAtual);

})
.catch(err => console.error("Erro:", err));