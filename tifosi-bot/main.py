import json
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from parser import parse_resultado
from image_generator import generar

TOKEN = "8768812473:AAGKL-wV_vCm0_poBml5MIxpQO5s55Vm9Sc"  # ⚠️ pon tu token real

print("🚀 Iniciando bot...")


# =========================
# COMANDO /start
# =========================
async def start(update, context):
    await update.message.reply_text("Bot activo ✅")


# =========================
# MENSAJES DE TEXTO
# =========================
async def manejar_texto(update, context):
    texto = update.message.text
    print("📩 Mensaje recibido:", texto)

    try:
        data = parse_resultado(texto)

        # ✅ GENERAR IMAGEN
        ruta_img = generar(data)

        # =========================
        # ✅ RESULTADOS
        # =========================
        with open("data/resultados.json", "r+") as f:
            datos = json.load(f)
            datos.append(data)
            f.seek(0)
            json.dump(datos, f, indent=2)

        # =========================
        # ✅ GOLEADORES
        # =========================
        with open("data/goleadores.json", "r+") as f:
            ranking = json.load(f)

            for nombre, goles in data["goleadores"]:
                encontrado = False

                for j in ranking:
                    if j["nombre"] == nombre:
                        j["goles"] += goles
                        encontrado = True

                if not encontrado:
                    ranking.append({
                        "nombre": nombre,
                        "goles": goles
                    })

            f.seek(0)
            json.dump(ranking, f, indent=2)

        # =========================
        # ✅ CLASIFICACIÓN
        # =========================
        with open("data/clasificacion.json", "r+") as f:
            tabla = json.load(f)

            def actualizar(equipo, gf, gc):

                for t in tabla:
                    if t["equipo"] == equipo:
                        t["pj"] += 1
                        t["gf"] += gf
                        t["gc"] += gc

                        if gf > gc:
                            t["pts"] += 3
                        elif gf == gc:
                            t["pts"] += 1
                        return

                # nuevo equipo
                tabla.append({
                    "equipo": equipo,
                    "pj": 1,
                    "gf": gf,
                    "gc": gc,
                    "pts": 3 if gf > gc else 1 if gf == gc else 0
                })

            actualizar(data["local"], data["goles_local"], data["goles_visitante"])
            actualizar(data["visitante"], data["goles_visitante"], data["goles_local"])

            f.seek(0)
            json.dump(tabla, f, indent=2)

        # =========================
        # ✅ RESPUESTA BOT
        # =========================
        await update.message.reply_photo(photo=open(ruta_img, "rb"))

    except Exception as e:
        print("❌ Error:", e)
        await update.message.reply_text("Error procesando el mensaje")


# =========================
# CONFIG BOT
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_texto))

print("✅ Bot arrancado correctamente")

app.run_polling()