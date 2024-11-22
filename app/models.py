from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey,UniqueConstraint
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# from app.database import Base;
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from settings import DB_USER

Base = declarative_base()

class AuditMixin:
    created_by = Column(String(100), nullable=False, default=DB_USER)
    updated_by = Column(String(100), nullable=False, default=DB_USER)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

# Table for Businesses
class Business(Base, AuditMixin):
    __tablename__ = "businesses"

    business_id = Column(Integer, primary_key=True, autoincrement=False)  # No auto-increment to match schema
    business_name = Column(String(255), nullable=False)

    # created_at = Column(DateTime, default=func.now(), nullable=False)
    # updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    # Relationship to Business_Symptoms
    business_symptoms = relationship("BusinessSymptom", back_populates="business")


# Table for Symptoms
class Symptom(Base, AuditMixin):
    __tablename__ = "symptoms"

    symptom_code = Column(String(50), primary_key=True)
    symptom_name = Column(String(255), nullable=False)
    # created_at = Column(DateTime, default=func.now(), nullable=False)
    # updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to Business_Symptoms
    business_symptoms = relationship("BusinessSymptom", back_populates="symptom")




# Linking table for Businesses and Symptoms
class BusinessSymptom(Base, AuditMixin):
    __tablename__ = "business_symptoms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(Integer, ForeignKey("businesses.business_id"), nullable=False)
    symptom_code = Column(String(50), ForeignKey("symptoms.symptom_code"), nullable=False)
    symptom_diagnostic = Column(Boolean, nullable=False)

    # created_at = Column(DateTime, default=func.now(), nullable=False)
    # updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    __table_args__ = (UniqueConstraint('business_id', 'symptom_code', 'symptom_diagnostic', name='unique_business_symptom'),)
    
    # Relationships
    business = relationship("Business", back_populates="business_symptoms")
    symptom = relationship("Symptom", back_populates="business_symptoms")


