"""
SQLAlchemy models package
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models to register them with SQLAlchemy
from .user import User
from .patient import Patient
from .visit import PatientVisit
from .assessment import NursingAssessment, RadiologyAssessment
from .document import Document
from .form import FormDefinition, FormSubmission

__all__ = [
    "Base",
    "User",
    "Patient",
    "PatientVisit",
    "NursingAssessment",
    "RadiologyAssessment",
    "Document",
    "FormDefinition",
    "FormSubmission"
]