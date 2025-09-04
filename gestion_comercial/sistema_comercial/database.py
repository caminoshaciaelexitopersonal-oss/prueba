import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import os
import uuid
import datetime
import json
from models.data_models import Customer, Lead, Interaction, SupportTicket

# Define the database file path relative to this file
db_file = "sistema_comercial.db"
db_path = os.path.join(os.path.dirname(__file__), db_file)
engine = sa.create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)

metadata = sa.MetaData()

# --- Table Definitions ---

customers_table = sa.Table(
    "customers",
    metadata,
    sa.Column("id", sa.String, primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("name", sa.String, nullable=False),
    sa.Column("email", sa.String, unique=True),
    sa.Column("phone", sa.String),
    sa.Column("address", sa.String),
    sa.Column("age", sa.Integer),
    sa.Column("location", sa.String),
    sa.Column("interests", sa.String), # Storing list as JSON string
    sa.Column("status", sa.String, default="prospecto"),
    sa.Column("value_tier", sa.String, default="medio"),
    sa.Column("preferred_channel", sa.String),
    sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
)

interactions_table = sa.Table(
    "interactions",
    metadata,
    sa.Column("id", sa.String, primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("customer_id", sa.String, sa.ForeignKey("customers.id"), nullable=False),
    sa.Column("channel", sa.String),
    sa.Column("content", sa.Text),
    sa.Column("sentiment", sa.String),
    sa.Column("agent_id", sa.String),
    sa.Column("timestamp", sa.DateTime, default=sa.func.now()),
)

leads_table = sa.Table(
    "leads",
    metadata,
    sa.Column("id", sa.String, primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("customer_id", sa.String, sa.ForeignKey("customers.id"), nullable=False),
    sa.Column("source", sa.String),
    sa.Column("status", sa.String, default="nuevo"),
    sa.Column("pipeline_stage", sa.String, default="calificacion"),
    sa.Column("estimated_value", sa.Float, default=0.0),
    sa.Column("probability", sa.Float, default=0.1),
    sa.Column("assigned_agent_id", sa.String),
    sa.Column("created_at", sa.DateTime, default=sa.func.now()),
)

support_tickets_table = sa.Table(
    "support_tickets",
    metadata,
    sa.Column("id", sa.String, primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("customer_id", sa.String, sa.ForeignKey("customers.id"), nullable=False),
    sa.Column("status", sa.String, default="abierto"),
    sa.Column("priority", sa.String, default="media"),
    sa.Column("subject", sa.String),
    sa.Column("description", sa.Text),
    sa.Column("assigned_agent_id", sa.String),
    sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    sa.Column("resolved_at", sa.DateTime),
)


def init_db():
    """Creates all tables in the database."""
    metadata.create_all(engine)

# --- CRUD Functions for Customers ---

def add_customer(customer: Customer) -> Customer:
    with Session() as session:
        stmt = customers_table.insert().values(
            id=customer.id,
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            address=customer.address,
            age=customer.age,
            location=customer.location,
            interests=json.dumps(customer.interests),
            status=customer.status,
            value_tier=customer.value_tier,
            preferred_channel=customer.preferred_channel,
            created_at=customer.created_at,
            updated_at=customer.updated_at
        )
        session.execute(stmt)
        session.commit()
        return customer

def get_customer_by_id(customer_id: str) -> Optional[Customer]:
    with Session() as session:
        stmt = sa.select(customers_table).where(customers_table.c.id == customer_id)
        result = session.execute(stmt).first()
        if result:
            interests = json.loads(result.interests) if result.interests else []
            return Customer(**{**result._asdict(), "interests": interests})
        return None

def get_all_customers() -> List[Customer]:
    customers = []
    with Session() as session:
        stmt = sa.select(customers_table)
        for row in session.execute(stmt).fetchall():
            interests = json.loads(row.interests) if row.interests else []
            customers.append(Customer(**{**row._asdict(), "interests": interests}))
    return customers


if __name__ == "__main__":
    print("Initializing CRM database...")
    init_db()
    print("Database ready.")
