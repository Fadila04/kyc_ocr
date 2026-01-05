from datetime import datetime, date

def parse_date(date_str):
    """Convertit dd/mm/yyyy en objet date"""

    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except Exception:
        return None
    

# Calcul de l'age
def calculate_age(birth_date: date) -> int:
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# Validation des champs OCR
def validate_required_fields(ocr_data: dict) -> bool:
    required = [
        "nom",
        "prenom",
        "date_naissance",
        "date_expiration",
        "numero_document"
    ]
    return all(ocr_data.get(field) for field in required)



def validate_kyc_data(
    ocr_data: dict,
    user_data: dict
) -> dict:
    """
    Applique les règles métier KYC
    """
    errors = []

    # 1. Champs obligatoires
    if not validate_required_fields(ocr_data):
        errors.append("Champs OCR manquants")

    # 2. Dates valides
    birth_date = parse_date(ocr_data.get("date_naissance"))
    expiration_date = parse_date(ocr_data.get("date_expiration"))

    if not birth_date or not expiration_date:
        errors.append("Format de date invalide")

    # 3. Âge légal
    if birth_date:
        age = calculate_age(birth_date)
        if age < 18:
            errors.append("Utilisateur mineur")

    # 4. Document valide
    if expiration_date and expiration_date < date.today():
        errors.append("Document expiré")

    # 5. Cohérence user ↔ OCR
    if ocr_data.get("nom") and ocr_data["nom"] != user_data["nom"].upper():
        errors.append("Nom incohérent")

    if ocr_data.get("prenom") and ocr_data["prenom"] != user_data["prenom"].upper():
        errors.append("Prénom incohérent")

    # Score de confiance (simple)
    confidence_score = max(0, 1 - len(errors) * 0.2)

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "confidence_score": round(confidence_score, 2)
    }
