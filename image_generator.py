from PIL import Image, ImageDraw, ImageFont
import datetime

EQUIPO = "Tifosi"

# =========================
# FUNCIONES DE CENTRADO
# =========================
def center_text(draw, img, text, font, y, color):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (img.width - w) // 2
    draw.text((x, y), text, fill=color, font=font)

def center_text_x(draw, text, font, x, y, color):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text((x - w // 2, y), text, fill=color, font=font)

def center_multiline_text(draw, img, lines, font, y, color, spacing=10):
    total_height = 0
    heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        heights.append(h)
        total_height += h
    total_height += spacing * (len(lines) - 1)
    current_y = y - total_height // 2

    for line, height in zip(lines, heights):
        center_text(draw, img, line, font, current_y, color)
        current_y += height + spacing


def wrap_team_names(draw, text, font, max_width):
    bbox = draw.textbbox((0, 0), text, font=font)
    if bbox[2] - bbox[0] <= max_width:
        return [text]

    if " VS " in text:
        local, _, visitante = text.partition(" VS ")
        first_line = local
        second_line = f"VS {visitante}"
        bbox2 = draw.textbbox((0, 0), second_line, font=font)
        if bbox2[2] - bbox2[0] <= max_width:
            return [first_line, second_line]

        second_line = "VS"
        third_line = visitante
        return [first_line, second_line, third_line]

    return [text]


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]

# =========================
# GENERADOR
# =========================
def generar(data):
    equipo_local = data["local"]
    equipo_visitante = data["visitante"]
    goles_local = data["goles_local"]
    goles_visitante = data["goles_visitante"]
    goleadores = data["goleadores"]

    # =========================
    # RESULTADO
    # =========================
    if ((equipo_local == EQUIPO and goles_local > goles_visitante) or
        (equipo_visitante == EQUIPO and goles_visitante > goles_local)):
        resultado = "VICTORIA"
    elif goles_local == goles_visitante:
        resultado = "EMPATE"
    else:
        resultado = "DERROTA"

    COLOR_BEIGE = "#d6c2a1"
    COLOR_RESULTADO = {
        "VICTORIA": "#00c853",
        "EMPATE": "#9e9e9e",
        "DERROTA": "#ff3b30"
    }

    # =========================
    # IMAGEN BASE
    # =========================
    img = Image.open("plantilla.png").convert("RGBA")
    draw = ImageDraw.Draw(img)

    ancho, alto = img.size

    # =========================
    # POSICIONES
    # =========================
    y_titulo = int(alto * 0.05)
    y_jornada = int(alto * 0.12)
    y_estado = int(alto * 0.18)

    y_gol_arriba = int(alto * 0.40)
    y_gol_abajo = int(alto * 0.60)

    x_gol_arriba = int(ancho * 0.25)
    x_gol_abajo = int(ancho * 0.75)

    y_equipo_offset = int(alto * 0.06)

    # 🔥 ajuste fino bloque goleadores
    y_goleadores = int(alto * 0.88)

    # =========================
    # FUENTES
    # =========================
    font_titulo = ImageFont.truetype("fonts/Bauman-Regular.ttf", int(ancho * 0.08))
    font_estado = ImageFont.truetype("fonts/Bauman-Regular.ttf", int(ancho * 0.12))
    font_marcador = ImageFont.truetype("fonts/Bauman-Regular.ttf", int(ancho * 0.40))
    font_equipo = ImageFont.truetype("fonts/Bauman-Regular.ttf", int(ancho * 0.07))
    font_goleadores = ImageFont.truetype("fonts/Bauman-Regular.ttf", int(ancho * 0.045))
    font_jornada = ImageFont.truetype("fonts/Bauman-Regular.ttf", int(ancho * 0.055))

    # =========================
    # CABECERA
    # =========================
    center_text(draw, img, "RESULTADO", font_titulo, y_titulo, COLOR_BEIGE)

    texto_jornada = f"JORNADA {data['jornada']}"
    center_text(draw, img, texto_jornada, font_jornada, y_jornada, COLOR_BEIGE)

    center_text(draw, img, resultado, font_estado, y_estado, COLOR_RESULTADO[resultado])

    # =========================
    # ESCUDO
    # =========================
    escudo = Image.open("escudo.png").convert("RGBA")
    escudo_size = int(ancho * 0.18)
    escudo = escudo.resize((escudo_size, escudo_size), Image.LANCZOS)

    offset_x = 150 if equipo_local == EQUIPO else -150
    offset_y = -200

    if equipo_local == EQUIPO:
        img.paste(escudo,
                  (x_gol_arriba - escudo_size//2 + offset_x,
                   y_gol_arriba + offset_y),
                  escudo)
    else:
        img.paste(escudo,
                  (x_gol_abajo - escudo_size//2 + offset_x,
                   y_gol_abajo + offset_y),
                  escudo)

    # =========================
    # NOMBRES EQUIPOS
    # =========================
    center_text_x(draw, equipo_local.upper(),
                  font_equipo,
                  x_gol_arriba,
                  y_gol_arriba - y_equipo_offset,
                  COLOR_BEIGE)

    center_text_x(draw, equipo_visitante.upper(),
                  font_equipo,
                  x_gol_abajo,
                  y_gol_abajo - y_equipo_offset,
                  COLOR_BEIGE)

    # =========================
    # MARCADOR (SIN SOMBRA)
    # =========================
    center_text_x(draw, str(goles_local),
                font_marcador,
                x_gol_arriba,
                y_gol_arriba,
                COLOR_BEIGE)

    center_text_x(draw, str(goles_visitante),
                font_marcador,
                x_gol_abajo,
                y_gol_abajo,
                COLOR_BEIGE)


    # =========================
    # GOLEADORES (CHIPS PRO)
    # =========================
    chip_padding_x = 20
    chip_padding_y = 10
    chip_spacing = 25

    # 🔥 color mejorado
    COLOR_CHIP = (87, 52, 0, 200)

    max_width = int(ancho * 0.85)

    chips = []
    for nombre, goles in goleadores:
        texto = f"[{goles}] {nombre.upper()}"

        bbox = draw.textbbox((0, 0), texto, font=font_goleadores)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        chip_w = text_w + chip_padding_x * 2
        chip_h = text_h + chip_padding_y * 2

        chips.append((texto, chip_w, chip_h))

    filas = []
    fila_actual = []
    ancho_fila = 0

    for chip in chips:
        texto, chip_w, chip_h = chip

        if ancho_fila + chip_w + chip_spacing > max_width and fila_actual:
            filas.append(fila_actual)
            fila_actual = [chip]
            ancho_fila = chip_w + chip_spacing
        else:
            fila_actual.append(chip)
            ancho_fila += chip_w + chip_spacing

    if fila_actual:
        filas.append(fila_actual)

    y_actual = y_goleadores

    for fila in filas:

        total_w = sum(chip[1] for chip in fila) + chip_spacing * (len(fila) - 1)
        x_actual = (ancho - total_w) // 2

        for texto, chip_w, chip_h in fila:

            # fondo + borde
            draw.rounded_rectangle(
                [
                    (x_actual, y_actual),
                    (x_actual + chip_w, y_actual + chip_h)
                ],
                radius=20,
                fill=COLOR_CHIP,
                outline="#d6c2a1",
                width=2
            )

            draw.text(
                (x_actual + chip_padding_x,
                 y_actual + chip_padding_y),
                texto,
                fill=COLOR_BEIGE,
                font=font_goleadores
            )

            x_actual += chip_w + chip_spacing

        y_actual += chip_h + 10

    # =========================
    # EXPORTAR
    # =========================
    ruta = f"imagenes/jornada_{data['jornada']}.png"
    
    # Guardado principal
    img.save(ruta)

    # 📱 versión cuadrada Instagram
    img_square = img.resize((1080, 1080))
    img_square.save(f"imagenes/jornada_{data['jornada']}_ig.png")

    # 📲 versión story (vertical)
    img_story = img.resize((1080, 1920))
    img_story.save(f"imagenes/jornada_{data['jornada']}_story.png")


    return ruta


def generar_proximo(data):
    fecha = data["fecha"]
    hora = data["hora"]
    equipo_local = data["local"]
    equipo_visitante = data["visitante"]
    ubicacion = data.get("ubicacion", "").strip() or "CDM MARGOT MOLES, VICALVARO"

    # Formatear fecha
    if fecha != "Fecha no definida":
        try:
            fecha_obj = datetime.datetime.strptime(fecha, "%Y-%m-%d")
            fecha_formateada = fecha_obj.strftime("%d/%m/%y")
        except ValueError:
            fecha_formateada = fecha
    else:
        fecha_formateada = fecha

    COLOR_BEIGE = "#d6c2a1"

    img = Image.open("plantilla.png").convert("RGBA")
    draw = ImageDraw.Draw(img)
    ancho, alto = img.size

    # =========================
    # POSICIONES
    # =========================
    y_jornada = int(alto * 0.10)
    y_fecha = int(alto * 0.20)
    y_equipos = int(alto * 0.35)
    y_escudo = int(alto * 0.55)
    y_ubicacion = int(alto * 0.83)

    # =========================
    # FUENTES
    # =========================
    font_jornada = ImageFont.truetype("fonts/Bauman-Regular.ttf", int(ancho * 0.1))
    font_fecha = ImageFont.truetype("fonts/Bauman-Regular.ttf", int(ancho * 0.08))
    font_equipo = ImageFont.truetype("fonts/Bauman-Regular.ttf", int(ancho * 0.15))
    font_ubicacion = ImageFont.truetype("fonts/Bauman-Regular.ttf", int(ancho * 0.042))

    # =========================
    # TEXTO PRINCIPAL
    # =========================
    center_text(draw, img, f"JORNADA {data['jornada']}", font_jornada, y_jornada, COLOR_BEIGE)
    center_text(draw, img, f"{fecha_formateada} {hora}", font_fecha, y_fecha, COLOR_BEIGE)

    # Equipos en líneas separadas centradas
    spacing = int(alto * 0.06)
    center_text(draw, img, equipo_local.upper(), font_equipo, y_equipos - spacing, COLOR_BEIGE)
    center_text(draw, img, "\nVS", font_equipo, y_equipos, COLOR_BEIGE)
    center_text(draw, img, "\n" + equipo_visitante.upper(), font_equipo, y_equipos + spacing, COLOR_BEIGE)

    # =========================
    # ESCUDO
    # =========================
    escudo = Image.open("escudo.png").convert("RGBA")
    escudo_size = int(ancho * 0.30)
    escudo = escudo.resize((escudo_size, escudo_size), Image.LANCZOS)
    x_escudo = (ancho - escudo_size) // 2
    img.paste(escudo, (x_escudo, y_escudo), escudo)

    # =========================
    # UBICACIÓN
    # =========================
    ubicacion_lines = wrap_text(draw, ubicacion.upper(), font_ubicacion, int(ancho * 0.85))
    center_multiline_text(draw, img, ubicacion_lines, font_ubicacion, y_ubicacion, COLOR_BEIGE, spacing=8)

    # =========================
    # EXPORTAR
    # =========================
    ruta = f"imagenes/proximo_jornada_{data['jornada']}.png"
    img.save(ruta)

    img_square = img.resize((1080, 1080))
    img_square.save(f"imagenes/proximo_jornada_{data['jornada']}_ig.png")

    img_story = img.resize((1080, 1920))
    img_story.save(f"imagenes/proximo_jornada_{data['jornada']}_story.png")

    return ruta