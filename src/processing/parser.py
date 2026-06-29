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

    # Detectar línea de encabezado
    header_line = None
    for line in lines:
        if re.search(r'\b(pos|equipo|j|g|e|p|gf|gc|dif|pts)\b', line, re.I):
            header_line = line
            break

    num_columns = []
    if header_line:
        header_tokens = re.findall(r'\b\w+\b', header_line.lower())
        for token in header_tokens:
            if token in ['j', 'pj']:
                num_columns.append('pj')
            elif token == 'g':
                num_columns.append('g')
            elif token == 'e':
                num_columns.append('e')
            elif token == 'p':
                num_columns.append('p')
            elif token in ['gf', 'favor']:
                num_columns.append('favor')
            elif token in ['gc', 'contra']:
                num_columns.append('contra')
            elif token == 'dif':
                num_columns.append('dif')
            elif token == 'pts':
                num_columns.append('pts')

    clasificacion = []
    for line in lines:
        if header_line and line == header_line:
            continue
        if not line or re.search(r'Clasificaci|Equipo|Pts|Fase|Grupo|MuniM@d', line, re.I):
            continue

        match = re.match(r'^\D*(\d+)[\W_]*(.+)$', line)
        if not match:
            continue

        pos = int(match.group(1))
        rest = re.sub(r'^[\W_]+', '', match.group(2)).strip()
        tokens = rest.split()
        if not tokens:
            continue

        # Extraer números desde el final
        numbers = []
        i = len(tokens) - 1
        while i >= 0:
            cleaned = re.sub(r'[^\d]', '', tokens[i])
            if cleaned.isdigit():
                numbers.insert(0, int(cleaned))
                i -= 1
            else:
                break

        if len(numbers) < 2:
            continue

        equipo = ' '.join(tokens[:i + 1]).strip()
        equipo = re.sub(r'\s*@\s*$', '', equipo).strip()
        if not equipo:
            continue

        item = {"pos": pos, "equipo": equipo}

        if num_columns and len(numbers) == len(num_columns):
            for col, val in zip(num_columns, numbers):
                item[col] = val
        else:
            # Fallback al método antiguo
            pj = numbers[0]
            pts = numbers[-1]
            g = e = p = favor = contra = 0
            if len(numbers) == 7:
                g = numbers[1]
                e = numbers[2]
                p = numbers[3]
                favor = numbers[4]
                contra = numbers[5]
            elif len(numbers) >= 3:
                g = numbers[1]
                if len(numbers) >= 4:
                    e = numbers[2]
                if len(numbers) >= 5:
                    p = numbers[3]
            item.update({"pj": pj, "g": g, "e": e, "p": p, "favor": favor, "contra": contra, "pts": pts})

        # Calcular dif si no está presente
        if 'dif' not in item:
            favor = item.get('favor', 0)
            contra = item.get('contra', 0)
            item['dif'] = favor - contra

        clasificacion.append(item)

    clasificacion.sort(key=lambda x: x["pos"])
    return clasificacion


def parse_clasificacion_image(ruta_imagen):
    texto = leer_imagen(ruta_imagen)
    return parse_clasificacion_text(texto)
