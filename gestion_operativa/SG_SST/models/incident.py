import uuid
from dataclasses import dataclass, field
from datetime import date

@dataclass
class Incident:
    description: str
    location: str
    incident_date: date
    employee_id: str  # Foreign key to the Employee
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    severity: str = "N/A"

    def to_dict(self):
        return {
            "id": str(self.id),
            "employee_id": self.employee_id,
            "incident_date": self.incident_date.isoformat(),
            "location": self.location,
            "description": self.description,
            "severity": self.severity,
        }
