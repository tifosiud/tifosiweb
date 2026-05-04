import json
import os
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from parser import parse_resultado
from image_generator import generar

TOKEN = "8768812473:AAGKL-wV_vCm0_poBml5MIxpQO5s55Vm9Sc"

print("🚀 Iniciando bot...")


async def start(update, context):
    await update.message.reply_text("Bot activo ✅")


async def manejar_texto(update, context):
    texto = update.message.text
    print("📩 Mensaje recibido:", texto)

    try:
        tipo = texto[0].upper()

        # =========================
        # A → RESULTADO EQUIPO
        # =========================
        if tipo == "A":
            data = parse_resultado(texto[2:])
            ruta_img = generar(data)

            with open("data/resultados_equipo.json", "r+") as f:
                datos = json.load(f)
                datos.append(data)
                f.seek(0)
                json.dump(datos, f, indent=2)

            await update.message.reply_photo(photo=open(ruta_img, "rb"))

        # =========================
        # C → RESULTADOS LIGA
        # =========================
        elif tipo == "C":
            data = parse_resultado(texto[2:])

            with open("data/resultados_liga.json", "r+") as f:
                liga = json.load(f)
                liga.append(data)
                f.seek(0)
                json.dump(liga, f, indent=2)

            await update.message.reply_text("Resultado de liga guardado ✅")

        # =========================
        # B → CLASIFICACIÓN
        # =========================
        elif tipo == "B":
            data = json.loads(texto[2:])

            with open("data/clasificacion.json", "w") as f:
                json.dump(data, f, indent=2)

            await update.message.reply_text("Clasificación actualizada ✅")

        # =========================
        # P → PRÓXIMO PARTIDO
        # =========================
        elif tipo == "P":

            partes = texto.split(" ")

            jornada = int(partes[1][1:])
            local = partes[2]
            visitante = partes[4]
            hora = partes[5]

            with open("data/jornadas.json", "r") as f:
                jornadas = json.load(f)

            fecha = jornadas.get(str(jornada), "Fecha no definida")

            with open("data/proximo.json", "w") as f:
                json.dump({
                    "jornada": jornada,
                    "fecha": fecha,
                    "hora": hora,
                    "local": local,
                    "visitante": visitante
                }, f, indent=2)

            await update.message.reply_text("Próximo partido actualizado ✅")

        else:
            await update.message.reply_text("Formato no reconocido")

        # =========================
        # AUTO UPDATE WEB (SEGURA)
        # =========================
        os.system("git add .")
        os.system('git diff --cached --quiet || git commit -m "update web"')
        os.system("git push")

    except Exception as e:
        print("❌ Error:", e)
        await update.message.reply_text("Error procesando el mensaje")


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_texto))

print("✅ Bot arrancado correctamente")

app.run_polling()
