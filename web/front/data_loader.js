const imageCache = new Map();

export async function getJSON(url) {
  try {
    const response = await fetch(`${url}?t=${Date.now()}`);
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function buscarUltimaImagenInterna(tipo) {
  for (let jornada = 100; jornada >= 1; jornada--) {
    const ruta = `imagenes/j${jornada}/${tipo}/j${jornada}_${tipo}.png`;
    const cacheEntry = imageCache.get(ruta);
    if (cacheEntry) {
      return cacheEntry.existe ? { ruta, jornada } : null;
    }

    try {
      const img = new Image();
      const existe = await new Promise((resolve) => {
        img.onload = () => resolve(true);
        img.onerror = () => resolve(false);
        img.src = `${ruta}?t=${Date.now()}`;
      });
      imageCache.set(ruta, { existe, timestamp: Date.now() });
      if (existe) return { ruta, jornada };
    } catch (error) {
      imageCache.set(ruta, { existe: false, timestamp: Date.now() });
    }
  }
  return null;
}
