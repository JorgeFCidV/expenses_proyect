import os
import random
import string
import subprocess
from flask import current_app
from PIL import Image
import pytesseract
import re
from datetime import datetime
import fitz  # pymupdf

def save_picture(form_picture):
    random_hex = ''.join(random.choices(string.hexdigits.lower(), k=16))
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext.lower()
    picture_path = os.path.join(current_app.root_path, 'static', 'uploads', picture_fn)
    form_picture.save(picture_path)
    if f_ext.lower() != '.pdf':
        subprocess.run(['exiftran', '-ai', picture_path], check=False)
    return picture_fn

def ocr_process(image_path):
    text = ""
    if image_path.endswith('.pdf'):
        doc = fitz.open(image_path)
        for page in doc:
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text += pytesseract.image_to_string(img, lang='spa') + "\n"
        doc.close()
    else:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='spa')
    return text.strip() if text.strip() else "No se detectó texto legible"
