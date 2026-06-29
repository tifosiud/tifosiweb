import json
import re
from pathlib import Path


def parse_proximo_partido(texto, jornadas_path=None):
    match = re.match(r'P\s+J(\d+)\s+(.+?)\s+vs\s+(.+?)\s+(\d{1,2}:\d{2})(?:\s+(.+))?$', texto, re.I)
    if not match:
        raise ValueError("Formato de próximo partido no reconocido")

    jornada = int(match.group(1))
    local = match.group(2)
    visitante = match.group(3)
    hora = match.group(4)
    ubicacion = match.group(5) or "CDM MARGOT MOLES, VICALVARO"

    jornadas_file = Path(jornadas_path or "data/jornadas.json")
    with jornadas_file.open("r", encoding="utf-8") as f:
        jornadas = json.load(f)

    fecha = jornadas.get(str(jornada), "Fecha no definida")

    return {
        "jornada": jornada,
        "fecha": fecha,
        "hora": hora,
        "local": local,
        "visitante": visitante,
        "ubicacion": ubicacion,
    }
