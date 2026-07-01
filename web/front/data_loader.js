const latestAssetsCache = { promise: null };

export async function getJSON(url) {
  try {
    const response = await fetch(`${url}?t=${Date.now()}`);
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function buscarUltimaImagenInterna(tipo) {
  if (!latestAssetsCache.promise) {
    latestAssetsCache.promise = getJSON("/last_assets.json");
  }

  const assets = await latestAssetsCache.promise;
  if (!assets || typeof assets !== "object") {
    return null;
  }

  const ruta = assets[tipo];
  if (typeof ruta !== "string" || !ruta.trim()) {
    return null;
  }

  const jornadaMatch = ruta.match(/j(\d+)_/i);
  const jornada = jornadaMatch ? Number(jornadaMatch[1]) : null;
  return { ruta: `/${ruta.replace(/^\//, "")}`, jornada };
}
