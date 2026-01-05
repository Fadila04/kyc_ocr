from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import hashlib

from database.database import get_db
from database.models import User, Document, KYCLog
from services.ocr_service import extract_text_from_file, parse_kyc_data
from services.data_validation import validate_kyc_data
from services.fraud_detection import detect_fraud




app = FastAPI(title= "KYC API")

@app.post("/kyc/upload")
def upload_kyc(
    nom: str = Form(...),
    prenom: str = Form(...),
    date_naissance: date = Form(...),
    document_type: str = Form(...),
    expiration_date: date = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Vérification format fichier
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Format de document non supporté")

    # Lecture du fichier et hash (anti-fraude)
    file_bytes = file.file.seek(0)
    document_hash = hashlib.sha256(file_bytes).hexdigest()

    # Vérifier si document déjà utilisé
    existing_doc = db.query(Document).filter_by(document_hash=document_hash).first()
    if existing_doc:
        raise HTTPException(status_code=400, detail="Document déjà soumis")

    # Création utilisateur
    user = User(
        nom=nom.upper(),
        prenom=prenom.upper(),
        date_naissance=date_naissance
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Enregistrement document
    document = Document(
        user_id=user.id,
        document_type=document_type,
        document_hash=document_hash,
        expiration_date=expiration_date,
        status="pending"
    )
    db.add(document)

    # Log KYC
    log = KYCLog(
        user_id=user.id,
        step="UPLOAD",
        message="Document uploadé avec succès"
    )
    db.add(log)

    # OCR
    ocr_text = extract_text_from_file(file_bytes, file.content_type)
    extracted_data = parse_kyc_data(ocr_text)


    # Validation aprés OCR
    user_data = {
        "nom": nom,
        "prenom": prenom,
        "date_naissance": date_naissance
    }

    validation = validate_kyc_data(extracted_data, user_data)
    fraud_check = detect_fraud(
        user_data=user_data,
        document_hash=document_hash,
        user_id=user.id,
        db=db
)
    if fraud_check["is_fraud"]:
        document.status = "rejected"
    document.status = "validated" if validation["is_valid"] else "rejected"

    # Log KYC Validation
    log = KYCLog(
        user_id=user.id,
        step="VALIDATION",
        message="KYC validé" if validation["is_valid"] else f"KYC rejeté : {validation['errors']}"
    )
    db.add(log)

    # Log Fraude
    if fraud_check["is_fraud"]:
        db.add(KYCLog(
            user_id=user.id,
            step="FRAUD",
            message=f"Fraude détectée : {fraud_check['alerts']}"
    ))

    db.commit()

    return {
    "user_id": user.id,
   "kyc_status": document.status,
    "confidence_score": validation["confidence_score"],
    "errors": validation["errors"],
    "fraud_alerts": fraud_check["alerts"]
}
