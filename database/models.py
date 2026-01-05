from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    date_naissance = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    documents = relationship("Document", back_populates="user")
    logs = relationship("KYCLog", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    document_type = Column(String, nullable=False)
    document_hash = Column(String, unique=True, nullable=False)   # Pour la détection de fraude
    expiration_date = Column(Date, nullable=False)

    status = Column(String, default="pending")
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="documents")



class KYCLog(Base):
    __tablename__ = "kyc_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    step = Column(String, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="logs")

