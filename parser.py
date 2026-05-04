import re

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