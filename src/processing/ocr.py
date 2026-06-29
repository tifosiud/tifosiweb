import pytesseract
from PIL import Image, ImageFilter, ImageOps

def preprocess_image(ruta):
    img = Image.open(ruta)
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    img = img.filter(ImageFilter.MedianFilter(size=3))
    return img.point(lambda x: 0 if x < 180 else 255, mode="1")


def leer_imagen(ruta):
    img = preprocess_image(ruta)
    try:
        return pytesseract.image_to_string(img, lang="spa+eng", config='--psm 6')
    except pytesseract.TesseractError:
        return pytesseract.image_to_string(img, config='--psm 6')