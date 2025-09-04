import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Date,
    Enum,
    Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class ContractType(enum.Enum):
    INDEFINIDO = "Término Indefinido"
    FIJO = "Término Fijo"
    OBRA_LABOR = "Obra o Labor"

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(20), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contracts = relationship("Contract", back_populates="employee")

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    contract_type = Column(Enum(ContractType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date) # Puede ser nulo para contratos indefinidos
    salary = Column(Numeric(12, 2), nullable=False)
    is_active = Column(Integer, default=1) # 1 for active, 0 for inactive

    employee = relationship("Employee", back_populates="contracts")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


print("Modelos de la base de datos de Nómina definidos.")
