import uuid
from dataclasses import dataclass, field
from typing import List

@dataclass
class Risk:
    name: str
    description: str
    area: str
    risk_level: str  # e.g., "Bajo", "Medio", "Alto"
    controls: List[str] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "area": self.area,
            "risk_level": self.risk_level,
            "controls": ", ".join(self.controls), # Convert list to string for DB
        }
