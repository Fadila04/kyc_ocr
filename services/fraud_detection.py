from sqlalchemy.orm import Session
from database.models import Document, User
from database.models import KYCLog



def check_document_uniqueness(
    document_hash: str,
    db: Session
) -> list:
    """
    Vérifie si un document est déjà utilisé
    """
    alerts = []

    docs = db.query(Document).filter(
        Document.document_hash == document_hash
    ).all()

    if docs:
        for doc in docs:
            if doc.status == "validated":
                alerts.append("Document déjà validé pour un autre utilisateur")
            else:
                alerts.append("Document déjà soumis (statut non finalisé)")

    return alerts


def check_identity_reuse(
    user_data: dict,
    db: Session
) -> list:
    alerts = []

    users = db.query(User).filter(
        User.nom == user_data["nom"].upper(),
        User.prenom == user_data["prenom"].upper(),
        User.date_naissance == user_data["date_naissance"]
    ).all()

    if len(users) > 1:
        alerts.append("Même identité utilisée avec plusieurs comptes")
    return alerts


def check_failed_attempts(
    user_id: int,
    db: Session,
    max_attempts: int = 5
) -> list:
    alerts = []

    failed_logs = db.query(KYCLog).filter(
        KYCLog.user_id == user_id,
        KYCLog.step == "VALIDATION",
        KYCLog.message.like("%rejeté%")
    ).all()

    if len(failed_logs) >= max_attempts:
        alerts.append("Trop de tentatives KYC échouées")

    return alerts


def detect_fraud(
    user_data: dict,
    document_hash: str,
    user_id: int,
    db: Session
) -> dict:
    fraud_alerts = []

    fraud_alerts += check_document_uniqueness(document_hash, db)
    fraud_alerts += check_identity_reuse(user_data, db)
    fraud_alerts += check_failed_attempts(user_id, db)

    is_fraud = len(fraud_alerts) > 0

    return {
        "is_fraud": is_fraud,
        "alerts": fraud_alerts
    }
