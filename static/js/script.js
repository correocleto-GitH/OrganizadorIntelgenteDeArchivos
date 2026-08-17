const buscador = document.getElementById("buscador");
const filas = [...document.querySelectorAll("#tabla tr")];
let categoria = "Todas";

function filtrar() {
  const texto = (buscador?.value || "").toLowerCase();
  filas.forEach(f => {
    const nombre = f.cells[0].textContent.toLowerCase();
    const cat = f.dataset.cat;
    f.style.display = (nombre.includes(texto) && (categoria === "Todas" || cat === categoria)) ? "" : "none";
  });
}
buscador?.addEventListener("input", filtrar);
document.querySelectorAll(".filter").forEach(b => b.addEventListener("click", () => {
  document.querySelectorAll(".filter").forEach(x => x.classList.remove("active"));
  b.classList.add("active"); categoria = b.dataset.cat; filtrar();
}));
