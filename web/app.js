import { getJSON, buscarUltimaImagenInterna } from '/front/data_loader.js';
import { abbreviateTeam, renderList, showPlaceholder } from '/front/renderers.js';

let cargandoDatos = false;
let imagenesInicializadas = false;
const previousState = {
  proximo: null,
  resultadosEquipo: null,
  liga: null,
  clas: null,
  ultimaImagenResultadoRuta: null,
  ultimaImagenClasificacionRuta: null,
};
let clasificacionImgElement = null;

function datosIguales(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

function actualizarImagen(imgElement, ruta, container = null, placeholderMessage = '') {
  if (!ruta) {
    if (imgElement.dataset.currentSrc) {
      imgElement.dataset.currentSrc = '';
      imgElement.style.display = 'none';
      imgElement.removeAttribute('src');
      if (container) {
        showPlaceholder(container, placeholderMessage);
      }
    }
    return;
  }

  if (imgElement.dataset.currentSrc === ruta) {
    return;
  }

  const preload = new Image();
  preload.onload = () => {
    imgElement.src = `${ruta}?t=${Date.now()}`;
    imgElement.dataset.currentSrc = ruta;
    imgElement.style.display = 'block';
  };

  preload.onerror = () => {
    if (!imgElement.src && container) {
      imgElement.style.display = 'none';
      showPlaceholder(container, placeholderMessage);
    }
  };

  preload.src = ruta;
}

function actualizarClasificacionImagen(container, ruta) {
  if (!ruta) {
    if (clasificacionImgElement) {
      clasificacionImgElement.remove();
      clasificacionImgElement = null;
    }
    return false;
  }

  if (previousState.ultimaImagenClasificacionRuta === ruta && clasificacionImgElement) {
    return true;
  }

  const preload = new Image();
  preload.onload = () => {
    const nuevaImagen = document.createElement('img');
    nuevaImagen.src = `${ruta}?t=${Date.now()}`;
    nuevaImagen.alt = 'Clasificación';
    nuevaImagen.dataset.currentSrc = ruta;

    if (clasificacionImgElement) {
      container.replaceChild(nuevaImagen, clasificacionImgElement);
    } else {
      container.appendChild(nuevaImagen);
    }

    clasificacionImgElement = nuevaImagen;
  };

  preload.src = ruta;
  return true;
}

async function cargarDatos() {
  const proximo = await getJSON('/data/proximo.json');
  const imgProximo = document.getElementById('img-proximo');
  const proximoContainer = document.getElementById('proximo');

  if (!datosIguales(proximo, previousState.proximo)) {
    previousState.proximo = proximo;

    if (proximo && proximo.jornada) {
      actualizarImagen(
        imgProximo,
        `/imagenes/j${proximo.jornada}/info/j${proximo.jornada}_info.png`,
        proximoContainer,
        'No hay próximo partido definido'
      );
    } else {
      imgProximo.style.display = 'none';
      imgProximo.removeAttribute('src');
      showPlaceholder(proximoContainer, 'No hay próximo partido definido');
    }
  }

  const resultadosEquipo = await getJSON('/data/resultados_equipo.json');
  const ulEquipo = document.getElementById('equipo');
  if (!datosIguales(resultadosEquipo, previousState.resultadosEquipo)) {
    previousState.resultadosEquipo = resultadosEquipo;
    renderList(
      ulEquipo,
      Array.isArray(resultadosEquipo) ? resultadosEquipo : [],
      (item) => `${item.local} ${item.goles_local}-${item.goles_visitante} ${item.visitante}`
    );
  }

  const liga = await getJSON('/data/resultados_liga.json');
  const ulLiga = document.getElementById('liga');
  if (!datosIguales(liga, previousState.liga)) {
    previousState.liga = liga;
    renderList(
      ulLiga,
      Array.isArray(liga) ? liga : [],
      (item) => `${item.local} ${item.goles_local}-${item.goles_visitante} ${item.visitante}`
    );
  }

  const clas = await getJSON('/data/clasificacion.json');
  const contClasificacion = document.getElementById('clasificacion');

  if (!imagenesInicializadas) {
    const ultimaImagenResultado = await buscarUltimaImagenInterna('resultado');
    const imgResultado = document.getElementById('img');
    const resultadoRuta = ultimaImagenResultado?.ruta || null;
    previousState.ultimaImagenResultadoRuta = resultadoRuta;
    if (resultadoRuta) {
      actualizarImagen(imgResultado, resultadoRuta, null, 'No hay resultado disponible');
    } else {
      imgResultado.style.display = 'none';
      imgResultado.removeAttribute('src');
      showPlaceholder(contClasificacion, 'No hay resultado disponible');
    }

    const ultimaImagenClasificacion = await buscarUltimaImagenInterna('clasificacion');
    const clasificacionRuta = ultimaImagenClasificacion?.ruta || null;
    previousState.ultimaImagenClasificacionRuta = clasificacionRuta;
    if (clasificacionRuta) {
      actualizarClasificacionImagen(contClasificacion, clasificacionRuta);
    } else {
      contClasificacion.innerHTML = '';
    }

    imagenesInicializadas = true;
  }

  if (!datosIguales(clas, previousState.clas)) {
    previousState.clas = clas;
    contClasificacion.innerHTML = '';

    if (Array.isArray(clas) && clas.length) {
      const sortedClas = [...clas].sort((a, b) => b.pts - a.pts);
      const table = document.createElement('table');
      table.innerHTML = '<tr><th>#</th><th>Equipo</th><th>PJ</th><th>G</th><th>E</th><th>P</th><th>DIF</th><th>PTS</th></tr>';

      sortedClas.forEach((entry, index) => {
        const row = document.createElement('tr');
        if (entry.equipo && entry.equipo.trim().toLowerCase() === 'tifosi') {
          row.classList.add('tifosi');
        }

        row.innerHTML = `
          <td>${index + 1}</td>
          <td>${abbreviateTeam(entry.equipo)}</td>
          <td>${entry.pj}</td>
          <td>${entry.g || 0}</td>
          <td>${entry.e || 0}</td>
          <td>${entry.p || 0}</td>
          <td>${typeof entry.dif !== 'undefined' ? entry.dif : (entry.favor && entry.contra ? entry.favor - entry.contra : 0)}</td>
          <td>${entry.pts}</td>
        `;
        table.appendChild(row);
      });

      contClasificacion.appendChild(table);
    } else {
      showPlaceholder(contClasificacion, 'No hay clasificación disponible');
    }
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

window.addEventListener('DOMContentLoaded', iniciarRefresco);
