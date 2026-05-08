function abrirImagem(src) {
  document.getElementById("modalImg").style.display = "flex";
  document.getElementById("imgExpandida").src = src;
}

document.getElementById("modalImg").onclick = function() {
  this.style.display = "none";
}

// cores participantes
document.querySelectorAll("#tabela-participantes tr").forEach((linha, index) => {
    const cor = `hsl(${(index * 137) % 360}, 70%, 50%)`;

    const tdNome = linha.querySelector(".nome");
    const tdVendedor = linha.querySelector(".vendedor");

    tdNome.style.color = cor;
    tdNome.style.fontWeight = "bold";

    tdVendedor.style.color = cor;
    tdVendedor.style.fontWeight = "bold";
});

