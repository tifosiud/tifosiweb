import atexit
import asyncio
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from telegram.ext import Application, MessageHandler, filters, CommandHandler

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.secciones.resultados import parse_resultado
from src.secciones.clasificacion import parse_clasificacion_image
from src.secciones.proximo_partido import parse_proximo_partido
from src.secciones.resultados_jornada import cargar_resultados_jornada, guardar_resultados_jornada
from src.secciones.resultados_imagen import generar
from src.secciones.proximo_partido_imagen import generar_proximo
from src.secciones.clasificacion_imagen import generar_clasificacion

TOKEN = "8768812473:AAGKL-wV_vCm0_poBml5MIxpQO5s55Vm9Sc"
PID_FILE = ROOT_DIR / "tmp" / "bot.pid"

print("🚀 Iniciando bot...")


def actualizar_git():
    try:
        subprocess.run(["git", "add", "data", "imagenes"], cwd=str(ROOT_DIR), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=str(ROOT_DIR), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", "update web"], cwd=str(ROOT_DIR), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "push"], cwd=str(ROOT_DIR), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ Git actualizado")
        else:
            print("ℹ️ No hay cambios para publicar")
    except subprocess.CalledProcessError as e:
        print("⚠️ Error al actualizar Git:", e.stderr.decode().strip() or e)
    except Exception as e:
        print("⚠️ Error inesperado al actualizar Git:", e)


def ensure_single_instance():
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)

    existing_pid = None
    if PID_FILE.exists():
        try:
            with PID_FILE.open("r", encoding="utf-8") as f:
                existing_pid = int(f.read().strip())
        except (ValueError, FileNotFoundError):
            existing_pid = None

    if existing_pid and existing_pid > 0:
        try:
            os.kill(existing_pid, 0)
        except ProcessLookupError:
            existing_pid = None
        except PermissionError:
            existing_pid = None
        else:
            print("⚠️ Ya hay una instancia del bot en ejecución. Se detiene esta copia.")
            return False

    if PID_FILE.exists():
        try:
            PID_FILE.unlink()
        except OSError:
            pass

    with PID_FILE.open("w", encoding="utf-8") as f:
        f.write(str(os.getpid()))

    return True


def cleanup_pid_file():
    try:
        PID_FILE.unlink()
    except FileNotFoundError:
        pass


atexit.register(cleanup_pid_file)


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

            with (ROOT_DIR / "data" / "resultados_equipo.json").open("r+", encoding="utf-8") as f:
                datos = json.load(f)
                datos.append(data)
                f.seek(0)
                json.dump(datos, f, indent=2)

            await update.message.reply_photo(photo=open(ruta_img, "rb"))
            await asyncio.to_thread(actualizar_git)

        # =========================
        # C → RESULTADOS LIGA
        # =========================
        elif tipo == "C":
            data = parse_resultado(texto[2:])
            liga = cargar_resultados_jornada("data/resultados_liga.json")
            liga.append(data)
            guardar_resultados_jornada(liga, "data/resultados_liga.json")

            await update.message.reply_text("Resultado de liga guardado ✅")

        # =========================
        # B → CLASIFICACIÓN
        # =========================
        elif tipo == "B":
            data = json.loads(texto[2:])

            with (ROOT_DIR / "data" / "clasificacion.json").open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            await update.message.reply_text("Clasificación actualizada ✅")

        # =========================
        # P → PRÓXIMO PARTIDO
        # =========================
        elif tipo == "P":
            proximo_data = parse_proximo_partido(texto)

            with (ROOT_DIR / "data" / "proximo.json").open("w", encoding="utf-8") as f:
                json.dump(proximo_data, f, indent=2)

            ruta_img = generar_proximo(proximo_data)
            with open(ruta_img, "rb") as photo:
                await update.message.reply_photo(photo=photo)
            await update.message.reply_text("Próximo partido actualizado ✅")
            await asyncio.to_thread(actualizar_git)

        else:
            await update.message.reply_text("Formato no reconocido")

    except Exception as e:
        print("❌ Error:", e)
        await update.message.reply_text("Error procesando el mensaje")


async def manejar_foto(update, context):
    caption = (update.message.caption or "").strip()
    if not caption.upper().startswith("B"):
        await update.message.reply_text("Envía la imagen con el caption B para clasificación.")
        return

    jornada = None
    match = re.match(r'B\s+J?(\d+)', caption, re.I)
    if match:
        jornada = int(match.group(1))

    photos = update.message.photo
    if not photos:
        await update.message.reply_text("No encontré una foto para procesar.")
        return

    file = await photos[-1].get_file()
    (ROOT_DIR / "tmp").mkdir(parents=True, exist_ok=True)
    tmp_path = ROOT_DIR / "tmp" / f"clasificacion_{update.message.message_id}.jpg"
    await file.download_to_drive(custom_path=tmp_path)

    data = parse_clasificacion_image(tmp_path)
    try:
        os.remove(tmp_path)
    except OSError:
        pass

    if not data:
        await update.message.reply_text("No pude leer la imagen de clasificación.")
        return

    with open("data/clasificacion.json", "w") as f:
        json.dump(data, f, indent=2)

    if jornada is not None:
        ruta_img = generar_clasificacion(jornada, data)
        with open(ruta_img, "rb") as photo:
            await update.message.reply_photo(photo=photo)

    await update.message.reply_text("Clasificación actualizada ✅")
    await asyncio.to_thread(actualizar_git)


if not ensure_single_instance():
    sys.exit(0)

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, manejar_foto))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_texto))

print("✅ Bot arrancado correctamente")

app.run_polling()
