import uuid
from dataclasses import dataclass, field
from datetime import date

@dataclass
class Employee:
    name: str
    position: str
    salary: float
    start_date: date
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    is_active: bool = True

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "position": self.position,
            "salary": self.salary,
            "start_date": self.start_date.isoformat(),
            "is_active": self.is_active,
        }
