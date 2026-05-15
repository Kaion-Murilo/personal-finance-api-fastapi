const meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];
const dados = JSON.parse(document.getElementById("dados-mensal").textContent);

const receitas = dados.map(d => d.receitas);
const despesas = dados.map(d => d.despesas);
const saldos = dados.map(d => d.saldo);

new Chart(document.getElementById("graficoMensal"), {
  type: "bar",
  data: {
    labels: meses,
    datasets: [
      {
        label: "Receitas",
        data: receitas,
        borderWidth: 2,
        borderRadius: 6,
      },
      {
        label: "Despesas",
        data: despesas,
        borderWidth: 2,
        borderRadius: 6,
      },
      {
        label: "Saldo",
        data: saldos,
        borderWidth: 2,
        borderRadius: 8,
      },
    ],
  },
});