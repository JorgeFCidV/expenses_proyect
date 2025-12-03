import os
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import re
from app import app

def save_picture(form_picture):
    if form_picture and form_picture.filename:
        filename = secure_filename(form_picture.filename)
        if filename.lower().endswith(('.jpg', '.jpeg')):
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            output_size = (1024, 768)  # Resize para OCR mejor
            i = Image.open(form_picture)
            i.thumbnail(output_size)
            i.save(path)
            return filename
    return None

def ocr_process(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return {}
    
    text = pytesseract.image_to_string(Image.open(filepath), lang='spa')  # Español para España
    
    # Extracción simple con regex (mejora con ML después)
    amount_match = re.search(r'(\d+[,]\d{2})', text)
    amount = float(amount_match.group(1).replace(',', '.')) if amount_match else 0.0
    
    nif_match = re.search(r'(\d{8}[A-Z])', text)
    nif = nif_match.group(1) if nif_match else ''
    
    # Clasificación básica por keywords
    nature = 'Otros'
    if any(word in text.lower() for word in ['taxi', 'bus', 'tren']):
        nature = 'Transporte'
    elif any(word in text.lower() for word in ['hotel', 'alojamiento']):
        nature = 'Alojamiento'
    # Agrega más...
    
    return {
        'text': text,
        'amount': amount,
        'nif': nif,
        'nature': nature,
        'company_name': re.search(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)', text).group(1) if re.search(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)', text) else ''
    }
