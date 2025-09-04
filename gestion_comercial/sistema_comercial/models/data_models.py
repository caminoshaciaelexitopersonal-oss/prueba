import datetime
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any

# Centralized data classes to avoid circular imports between models.

@dataclass
class Customer:
    id: str
    name: str
    phone: str
    email: str
    status: str

@dataclass
class Product:
    id: str
    name: str
    price: float

@dataclass
class LineItem:
    product: Product
    quantity: int
    @property
    def total(self) -> float:
        return self.product.price * self.quantity

@dataclass
class Order:
    id: str
    customer_id: str
    status: str
    total_amount: float
    items: List[LineItem] = field(default_factory=list)

@dataclass
class ScheduledPost:
    id: str
    date: datetime.date
    content_type: str
    content_data: Dict[str, Any]
