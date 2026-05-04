import pytesseract
from PIL import Image

def leer_imagen(ruta):
    return pytesseract.image_to_string(Image.open(ruta))