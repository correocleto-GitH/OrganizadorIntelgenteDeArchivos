const buscador = document.getElementById("buscador");
const cuerpoTabla = document.getElementById("tabla");
const filas = [...document.querySelectorAll("#tabla tr")];
const UMBRAL_SSE = 100;
const modoServidor = filas.length > UMBRAL_SSE;
let categoria = "Todas";
let controladorBusqueda = null;

function interceptarOrganizar(evento) {
  if (!confirm("¿Deseas mover los archivos? Esta acción modificará la carpeta seleccionada.")) {
    return false;
  }

  const totalArchivos = document.querySelectorAll("#tabla tr").length;
  if (totalArchivos <= UMBRAL_SSE) {
    return true;
  }

  evento.preventDefault();

  const incluirSub = document.getElementById("incluir_subcarpetas")?.checked ? "1" : "0";
  const url = `/organizar/progreso?modo=ejecutar&incluir_subcarpetas=${incluirSub}`;

  const contenedor = document.getElementById("progreso-contenedor");
  const barra = document.getElementById("barra-progreso");
  const texto = document.getElementById("progreso-texto");
  const contador = document.getElementById("progreso-contador");
  const btnOrganizar = document.getElementById("btn-organizar");

  contenedor?.removeAttribute("hidden");
  if (btnOrganizar) btnOrganizar.disabled = true;
  if (barra) { barra.value = 0; barra.max = 100; }
  if (texto) texto.textContent = "Organizando archivos…";
  if (contador) contador.textContent = "";

  const fuente = new EventSource(url);

  fuente.onmessage = (e) => {
    let datos;
    try {
      datos = JSON.parse(e.data);
    } catch {
      return;
    }

    if (datos.error) {
      fuente.close();
      if (texto) texto.textContent = "❌ Error: " + datos.error;
      if (btnOrganizar) btnOrganizar.disabled = false;
      return;
    }

    if (datos.completado) {
      fuente.close();
      if (barra) { barra.max = datos.total || 100; barra.value = datos.total || 100; }
      if (texto) texto.textContent = `✅ ${datos.total} archivos organizados. Recargando…`;
      if (contador) contador.textContent = "";
      setTimeout(() => window.location.reload(), 1200);
      return;
    }

    if (datos.total && datos.actual !== undefined) {
      if (barra) { barra.max = datos.total; barra.value = datos.actual; }
      if (contador) contador.textContent = `${datos.actual} / ${datos.total}`;
    }
  };

  fuente.onerror = () => {
    fuente.close();
    if (texto) texto.textContent = "❌ Error de conexión al servidor.";
    if (btnOrganizar) btnOrganizar.disabled = false;
  };

  return false;
}

function filtrarCliente() {
  const texto = (buscador?.value || "").toLowerCase();
  filas.forEach(f => {
    const nombre = f.cells[0].textContent.toLowerCase();
    const cat = f.dataset.cat;
    f.style.display = (nombre.includes(texto) && (categoria === "Todas" || cat === categoria)) ? "" : "none";
  });
}

function _crearCelda(texto) {
  const td = document.createElement("td");
  td.textContent = texto;
  return td;
}

function construirFila(archivo) {
  const tr = document.createElement("tr");
  tr.dataset.cat = archivo.categoria;
  const badge = document.createElement("span");
  badge.className = "badge";
  badge.textContent = (archivo.icono || "") + " " + archivo.categoria;
  const tdCat = document.createElement("td");
  tdCat.appendChild(badge);
  tr.appendChild(_crearCelda(archivo.archivo));
  tr.appendChild(_crearCelda(archivo.extension || "—"));
  tr.appendChild(tdCat);
  return tr;
}

function mostrarCargando() {
  if (!cuerpoTabla) return;
  cuerpoTabla.innerHTML = '<tr><td colspan="3" style="text-align:center;color:var(--color-muted)">Buscando…</td></tr>';
}

function mostrarError() {
  if (!cuerpoTabla) return;
  cuerpoTabla.innerHTML = '<tr><td colspan="3" style="text-align:center;color:var(--color-muted)">Error al buscar. Intenta de nuevo.</td></tr>';
}

async function buscarServidor() {
  if (!cuerpoTabla) return;

  if (controladorBusqueda) {
    controladorBusqueda.abort();
  }
  controladorBusqueda = new AbortController();

  const termino = (buscador?.value || "").trim();
  const params = new URLSearchParams({ q: termino, categoria });
  const url = "/buscar?" + params.toString();

  mostrarCargando();

  try {
    const respuesta = await fetch(url, { signal: controladorBusqueda.signal });
    if (!respuesta.ok) throw new Error("respuesta no ok");
    const datos = await respuesta.json();

    cuerpoTabla.innerHTML = "";
    if (datos.archivos.length === 0) {
      cuerpoTabla.innerHTML = '<tr><td colspan="3" style="text-align:center;color:var(--color-muted)">Sin resultados.</td></tr>';
    } else {
      datos.archivos.forEach(a => cuerpoTabla.appendChild(construirFila(a)));
    }
  } catch (err) {
    if (err.name !== "AbortError") {
      mostrarError();
    }
  }
}

let temporizadorDebounce = null;
function buscarConDebounce() {
  clearTimeout(temporizadorDebounce);
  temporizadorDebounce = setTimeout(buscarServidor, 250);
}

if (modoServidor) {
  buscador?.addEventListener("input", buscarConDebounce);
} else {
  buscador?.addEventListener("input", filtrarCliente);
}

window.interceptarOrganizar = interceptarOrganizar;

document.querySelectorAll(".filter").forEach(b => b.addEventListener("click", () => {
  document.querySelectorAll(".filter").forEach(x => x.classList.remove("active"));
  b.classList.add("active");
  categoria = b.dataset.cat;
  if (modoServidor) {
    buscarServidor();
  } else {
    filtrarCliente();
  }
}));

const checkSubcarpetas = document.getElementById("incluir_subcarpetas");
const inputSubSimular  = document.getElementById("sub-simular");
const inputSubOrganizar = document.getElementById("sub-organizar");

function sincronizarSubcarpetas() {
  if (!checkSubcarpetas) return;
  const valor = checkSubcarpetas.checked ? "on" : "";
  if (inputSubSimular)   inputSubSimular.value   = valor;
  if (inputSubOrganizar) inputSubOrganizar.value = valor;
}

document.getElementById("form-simular")?.addEventListener("submit", sincronizarSubcarpetas);
document.getElementById("form-organizar")?.addEventListener("submit", sincronizarSubcarpetas);
