import datetime
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Customer:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    # Basic Info
    name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    # Segmentation Info
    age: Optional[int] = None
    location: str = ""
    interests: List[str] = field(default_factory=list)
    # Status Info
    status: str = "prospecto"  # prospecto, lead, cliente activo, inactivo, VIP
    value_tier: str = "medio" # alto, medio, bajo
    # Communication Preferences
    preferred_channel: Optional[str] = None # email, whatsapp, phone
    # Timestamps
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class Interaction:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    channel: str = "" # llamada, chat, correo, red social
    content: str = ""
    sentiment: Optional[str] = None # positivo, neutro, negativo
    agent_id: Optional[str] = None
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class Lead:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    source: str = "" # website, social media, referral
    status: str = "nuevo" # nuevo, contactado, calificando, cerrado ganado, cerrado perdido
    pipeline_stage: str = "calificacion"
    estimated_value: float = 0.0
    probability: float = 0.1 # Probabilidad de cierre
    assigned_agent_id: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class SupportTicket:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    status: str = "abierto" # abierto, en progreso, cerrado
    priority: str = "media" # alta, media, baja
    subject: str = ""
    description: str = ""
    assigned_agent_id: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    resolved_at: Optional[datetime.datetime] = None
