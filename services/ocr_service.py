import pytesseract
from PIL import Image
import re
import io
from pdf2image import convert_from_bytes

from services.image_prepro import preprocess_image

def extract_text_from_file(file_bytes: bytes, content_type: str) -> str:
    """
    Extrait le texte OCR depuis une image ou un PDF
    """
    text = ""

    if content_type == "application/pdf":
        images = convert_from_bytes(file_bytes)
        for img in images:
            img = preprocess_image(img)
            text += pytesseract.image_to_string(img, lang="fra")

    else:
        image = Image.open(io.BytesIO(file_bytes))
        image = preprocess_image(image)
        text = pytesseract.image_to_string(image, lang="fra")

    return text



def parse_kyc_data(ocr_text: str) -> dict:
    """
    Extraction des champs KYC depuis le texte OCR
    """
    data = {}

    # Nom & prénom (simplifié)
    name_match = re.search(r"NOM\s*[:\-]?\s*([A-Z]+)", ocr_text)
    firstname_match = re.search(r"PR[EÉ]NOM\s*[:\-]?\s*([A-Z]+)", ocr_text)

    # Dates
    birth_match = re.search(r"NAISSANCE\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})", ocr_text)
    expire_match = re.search(r"EXPIRATION\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})", ocr_text)

    # Numéro document
    id_match = re.search(r"\b[A-Z0-9]{8,12}\b", ocr_text)

    data["nom"] = name_match.group(1) if name_match else None
    data["prenom"] = firstname_match.group(1) if firstname_match else None
    data["date_naissance"] = birth_match.group(1) if birth_match else None
    data["date_expiration"] = expire_match.group(1) if expire_match else None
    data["numero_document"] = id_match.group(0) if id_match else None

    return data
