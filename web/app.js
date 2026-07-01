import { getJSON, buscarUltimaImagenInterna } from './front/data_loader.js';
import { abbreviateTeam, renderList, showPlaceholder } from './front/renderers.js';

let cargandoDatos = false;
let resultadoBuscado = false;
let clasificacionBuscada = false;
let ultimaImagenResultado = null;
let ultimaImagenClasificacion = null;

async function cargarDatos() {
  const proximo = await getJSON("data/proximo.json");
  const imgProximo = document.getElementById("img-proximo");
  const proximoContainer = document.getElementById("proximo");

  if (proximo && proximo.jornada) {
    imgProximo.src = `imagenes/j${proximo.jornada}/info/j${proximo.jornada}_info.png?t=${Date.now()}`;
    imgProximo.style.display = "block";
  } else {
    imgProximo.style.display = "none";
    imgProximo.removeAttribute("src");
    showPlaceholder(proximoContainer, "No hay próximo partido definido");
  }

  const resultadosEquipo = await getJSON("data/resultados_equipo.json");
  const ulEquipo = document.getElementById("equipo");
  renderList(
    ulEquipo,
    Array.isArray(resultadosEquipo) ? resultadosEquipo : [],
    (item) => `${item.local} ${item.goles_local}-${item.goles_visitante} ${item.visitante}`
  );

  const liga = await getJSON("data/resultados_liga.json");
  const ulLiga = document.getElementById("liga");
  renderList(
    ulLiga,
    Array.isArray(liga) ? liga : [],
    (item) => `${item.local} ${item.goles_local}-${item.goles_visitante} ${item.visitante}`
  );

  const clas = await getJSON("data/clasificacion.json");
  const contClasificacion = document.getElementById("clasificacion");
  contClasificacion.innerHTML = "";

  if (!resultadoBuscado) {
    resultadoBuscado = true;
    ultimaImagenResultado = await buscarUltimaImagenInterna("resultado");
  }

  const imgResultado = document.getElementById("img");
  if (ultimaImagenResultado) {
    imgResultado.src = `${ultimaImagenResultado.ruta}?t=${Date.now()}`;
    imgResultado.style.display = "block";
  } else {
    imgResultado.style.display = "none";
    imgResultado.removeAttribute("src");
    showPlaceholder(contClasificacion, "No hay resultado disponible");
  }

  if (!clasificacionBuscada) {
    clasificacionBuscada = true;
    ultimaImagenClasificacion = await buscarUltimaImagenInterna("clasificacion");
  }

  if (ultimaImagenClasificacion) {
    const imgClasificacion = document.createElement("img");
    imgClasificacion.src = `${ultimaImagenClasificacion.ruta}?t=${Date.now()}`;
    imgClasificacion.alt = "Clasificación";
    contClasificacion.appendChild(imgClasificacion);
    return;
  }

  if (Array.isArray(clas) && clas.length) {
    const sortedClas = [...clas].sort((a, b) => b.pts - a.pts);
    const table = document.createElement("table");
    table.innerHTML = "<tr><th>#</th><th>Equipo</th><th>PJ</th><th>G</th><th>E</th><th>P</th><th>DIF</th><th>PTS</th></tr>";

    sortedClas.forEach((entry, index) => {
      const row = document.createElement("tr");
      if (entry.equipo && entry.equipo.trim().toLowerCase() === "tifosi") {
        row.classList.add("tifosi");
      }

      row.innerHTML = `
        <td>${index + 1}</td>
        <td>${abbreviateTeam(entry.equipo)}</td>
        <td>${entry.pj}</td>
        <td>${entry.g || 0}</td>
        <td>${entry.e || 0}</td>
        <td>${entry.p || 0}</td>
        <td>${typeof entry.dif !== "undefined" ? entry.dif : (entry.favor && entry.contra ? entry.favor - entry.contra : 0)}</td>
        <td>${entry.pts}</td>
      `;
      table.appendChild(row);
    });

    contClasificacion.appendChild(table);
  } else {
    showPlaceholder(contClasificacion, "No hay clasificación disponible");
  }
}

async function iniciarRefresco() {
  if (cargandoDatos) return;
  cargandoDatos = true;
  try {
    await cargarDatos();
  } finally {
    cargandoDatos = false;
    setTimeout(iniciarRefresco, 5000);
  }
}

window.addEventListener("DOMContentLoaded", iniciarRefresco);
