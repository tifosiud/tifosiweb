import re

import pytesseract
from PIL import Image, ImageFilter, ImageOps


def _prepare_gray_image(ruta):
    img = Image.open(ruta)
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.MedianFilter(size=3))
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    return img.filter(ImageFilter.GaussianBlur(radius=0.5))


def _remove_grid_lines(img):
    img = img.convert("1")
    width, height = img.size
    cleaned = img.copy()

    for y in range(height):
        dark_pixels = sum(1 for x in range(width) if cleaned.getpixel((x, y)) == 0)
        if dark_pixels > width * 0.8:
            for x in range(width):
                cleaned.putpixel((x, y), 255)

    for x in range(width):
        dark_pixels = sum(1 for y in range(height) if cleaned.getpixel((x, y)) == 0)
        if dark_pixels > height * 0.8:
            for y in range(height):
                cleaned.putpixel((x, y), 255)

    return cleaned


def _otsu_threshold(img):
    histogram = img.histogram()
    total_pixels = img.width * img.height
    sum_total = sum(i * histogram[i] for i in range(256))

    sum_background = 0
    weight_background = 0
    best_threshold = 0
    best_variance = 0.0

    for threshold in range(256):
        weight_background += histogram[threshold]
        if weight_background == 0:
            continue

        weight_foreground = total_pixels - weight_background
        if weight_foreground == 0:
            break

        sum_background += threshold * histogram[threshold]
        mean_background = sum_background / weight_background
        mean_foreground = (sum_total - sum_background) / weight_foreground

        variance_between = weight_background * weight_foreground * ((mean_background - mean_foreground) ** 2)
        if variance_between > best_variance:
            best_variance = variance_between
            best_threshold = threshold

    return best_threshold


def preprocess_image(ruta):
    img = _prepare_gray_image(ruta)
    threshold = _otsu_threshold(img)
    return img.point(lambda x: 0 if x < threshold else 255, mode="1")


def _to_binary(img, threshold=None):
    if threshold is None:
        threshold = _otsu_threshold(img)
    return img.point(lambda x: 0 if x < threshold else 255, mode="1")


def _ocr_with_image(img, lang="spa+eng", psm=6):
    try:
        return pytesseract.image_to_string(img, lang=lang, config=f"--oem 3 --psm {psm}")
    except pytesseract.TesseractError:
        return pytesseract.image_to_string(img, config=f"--psm {psm}")


def _score_text(text):
    cleaned = text.lower().replace("\n", " ")
    score = len(cleaned.strip())
    if any(token in cleaned for token in ["tifosi", "betis", "equipo", "pts", "clasificacion"]):
        score += 40
    if re.search(r"\b\d+\b", cleaned):
        score += 15
    if re.search(r"\b(?:pj|g|e|p|gf|gc|dif|pts)\b", cleaned):
        score += 20
    return score


def leer_imagen(ruta):
    gray = _prepare_gray_image(ruta)
    gray_2x = gray.resize((gray.width * 2, gray.height * 2), Image.LANCZOS)

    candidates = [gray_2x, preprocess_image(ruta), gray]
    if gray_2x.size[0] > 0:
        candidates.insert(0, _remove_grid_lines(gray_2x))
    candidates.extend([
        _to_binary(gray),
        _to_binary(gray_2x),
        _remove_grid_lines(gray),
        _remove_grid_lines(gray_2x),
    ])

    inverted = ImageOps.invert(gray)
    inverted_2x = ImageOps.invert(gray_2x)
    candidates.extend([
        _to_binary(inverted),
        _to_binary(inverted_2x),
    ])

    equalized = ImageOps.equalize(gray)
    equalized_2x = ImageOps.equalize(gray_2x)
    candidates.extend([
        _to_binary(equalized),
        _to_binary(equalized_2x),
    ])

    best_text = ""
    best_score = -1
    for candidate in candidates:
        for psm in [6, 11, 4, 12]:
            text = _ocr_with_image(candidate, psm=psm)
            score = _score_text(text)
            if score > best_score:
                best_text = text
                best_score = score

    if best_score < 50:
        large = gray.resize((gray.width * 4, gray.height * 4), Image.LANCZOS)
        for psm in [6, 11, 4, 12]:
            text = _ocr_with_image(large, psm=psm)
            score = _score_text(text)
            if score > best_score:
                best_text = text
                best_score = score

    return best_text