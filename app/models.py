from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy.orm import relationship
# from app.database import Base;
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
# Base = declarative_base()
from settings import DB_USER

Base = declarative_base()



# Table for Businesses
class Business(Base):
    __tablename__ = "businesses"

    business_id = Column(Integer, primary_key=True, autoincrement=False)  # No auto-increment to match schema
    business_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    # Relationship to Business_Symptoms
    business_symptoms = relationship("BusinessSymptom", back_populates="business")


# Table for Symptoms


class Symptom(Base):
    __tablename__ = "symptoms"

    symptom_code = Column(String(50), primary_key=True)
    symptom_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to Business_Symptoms
    business_symptoms = relationship("BusinessSymptom", back_populates="symptom")




# Linking table for Businesses and Symptoms
class BusinessSymptom(Base):
    __tablename__ = "business_symptoms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(Integer, ForeignKey("businesses.business_id"), nullable=False)
    symptom_code = Column(String(50), ForeignKey("symptoms.symptom_code"), nullable=False)
    symptom_diagnostic = Column(Boolean, nullable=False)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    business = relationship("Business", back_populates="business_symptoms")
    symptom = relationship("Symptom", back_populates="business_symptoms")


