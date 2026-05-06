import re
import unicodedata
from ocr import leer_imagen


def normalize_text(texto):
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(ch for ch in texto if unicodedata.category(ch) != 'Mn')
    return texto.replace('Ñ', 'N').replace('ñ', 'n')


def parse_resultado(texto):
    jornada = int(re.search(r'J(\d+)', texto).group(1))

    m = re.search(r'J\d+\s+(\w+)\s+(\d+)-(\d+)\s+(\w+)', texto)
    local, gl, gv, visitante = m.groups()

    goles = re.findall(r'(\w+)\((\d+)\)', texto)
    goleadores = [(n, int(g)) for n,g in goles]

    return {
        "jornada": jornada,
        "local": local,
        "visitante": visitante,
        "goles_local": int(gl),
        "goles_visitante": int(gv),
        "goleadores": goleadores
    }


def parse_clasificacion_text(texto):
    texto = normalize_text(texto.replace('\xa0', ' '))
    lines = [re.sub(r'\s+', ' ', line).strip() for line in texto.splitlines()]

    clasificacion = []
    for line in lines:
        if not line or re.search(r'Clasificaci|Equipo|Pts|Fase|Grupo|MuniM@d', line, re.I):
            continue

        parts = line.split()
        if not parts[0].isdigit():
            continue

        pos = int(parts[0])
        rest_tokens = parts[1:]
        if not rest_tokens:
            continue

        trailing = []
        i = len(rest_tokens) - 1
        while i >= 0 and rest_tokens[i].isdigit():
            trailing.insert(0, rest_tokens[i])
            i -= 1

        if len(trailing) < 2:
            continue

        equipo = ' '.join(rest_tokens[: i + 1]).strip()
        equipo = re.sub(r'\s*@\s*$', '', equipo).strip()
        if not equipo:
            continue

        pj = int(trailing[0])
        pts = int(trailing[-1])
        g = e = p = favor = contra = 0

        if len(trailing) == 7:
            g = int(trailing[1])
            e = int(trailing[2])
            p = int(trailing[3])
            favor = int(trailing[4])
            contra = int(trailing[5])
        elif len(trailing) >= 3:
            g = int(trailing[1])
            if len(trailing) >= 4:
                e = int(trailing[2])
            if len(trailing) >= 5:
                p = int(trailing[3])

        clasificacion.append({
            "pos": pos,
            "equipo": equipo,
            "pj": pj,
            "g": g,
            "e": e,
            "p": p,
            "favor": favor,
            "contra": contra,
            "pts": pts
        })

    clasificacion.sort(key=lambda x: x["pos"])
    return clasificacion


def parse_clasificacion_image(ruta_imagen):
    texto = leer_imagen(ruta_imagen)
    return parse_clasificacion_text(texto)
