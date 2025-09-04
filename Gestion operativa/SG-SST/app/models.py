import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Date,
    Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False)
    hire_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    inspections_conducted = relationship("Inspection", back_populates="inspector")

class InspectionStatus(enum.Enum):
    PLANNED = "Planeada"
    IN_PROGRESS = "En Progreso"
    COMPLETED = "Completada"
    CLOSED = "Cerrada"

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String(200), nullable=False)
    inspection_date = Column(DateTime(timezone=True), default=func.now())
    status = Column(Enum(InspectionStatus), default=InspectionStatus.PLANNED)
    findings = Column(Text)

    inspector_id = Column(Integer, ForeignKey("employees.id"))
    inspector = relationship("Employee", back_populates="inspections_conducted")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

print("Modelos de la base de datos de SG-SST definidos.")
