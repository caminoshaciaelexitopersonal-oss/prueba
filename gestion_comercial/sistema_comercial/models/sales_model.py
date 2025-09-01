# gestion_comercial/sistema_comercial/models/sales_model.py
from typing import Optional
from sqlalchemy import select
from dotenv import load_dotenv

from gestion_comercial.sistema_comercial.database import Session, customers_table

load_dotenv()

class SalesModel:
    """
    Este modelo ahora contiene la lógica de negocio relacionada con ventas
    que no está directamente implementada como una herramienta de agente.
    """
    def __init__(self, invoicing_model=None):
        # La dependencia de invoicing_model se mantiene por si se necesita en el futuro
        # para lógica de negocio compleja que una modelos.
        self.invoicing_model = invoicing_model

    def get_customer_by_id(self, customer_id: str) -> Optional[dict]:
        """
        Obtiene los detalles de un cliente por su ID.
        """
        with Session() as session:
            stmt = select(customers_table).where(customers_table.c.id == customer_id)
            result = session.execute(stmt).first()
            return result._asdict() if result else None
