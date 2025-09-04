import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import os
import uuid
import datetime
import json

# Define the database file path relative to this file
db_file = "sistema_comercial.db"
db_path = os.path.join(os.path.dirname(__file__), db_file)
engine = sa.create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)

metadata = sa.MetaData()

# Define tables using SQLAlchemy Core
customers_table = sa.Table(
    "customers",
    metadata,
    sa.Column("id", sa.String, primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("name", sa.String, nullable=False),
    sa.Column("phone", sa.String),
    sa.Column("email", sa.String),
    sa.Column("status", sa.String, default="Nuevo"),
)

products_table = sa.Table(
    "products",
    metadata,
    sa.Column("id", sa.String, primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("name", sa.String, nullable=False, unique=True),
    sa.Column("price", sa.Float, nullable=False),
)

orders_table = sa.Table(
    "orders",
    metadata,
    sa.Column("id", sa.String, primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("customer_id", sa.String, sa.ForeignKey("customers.id"), nullable=False),
    sa.Column("status", sa.String, default="pending"), # pending -> completed -> invoiced
    sa.Column("total_amount", sa.Float, default=0.0),
    sa.Column("created_at", sa.DateTime, default=sa.func.now()),
)

line_items_table = sa.Table(
    "line_items",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("order_id", sa.String, sa.ForeignKey("orders.id"), nullable=False),
    sa.Column("product_id", sa.String, sa.ForeignKey("products.id"), nullable=False),
    sa.Column("quantity", sa.Integer, nullable=False),
    sa.Column("total", sa.Float, nullable=False),
)

scheduled_posts_table = sa.Table(
    "scheduled_posts",
    metadata,
    sa.Column("id", sa.String, primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("date", sa.Date, nullable=False),
    sa.Column("content_type", sa.String, nullable=False),
    sa.Column("content_data_json", sa.String, nullable=False), # Store dict as JSON string
)

def init_db():
    """Creates all tables in the database and seeds initial data if necessary."""
    metadata.create_all(engine)

    with Session() as session:
        if session.query(customers_table).count() == 0:
            print("Seeding database with initial data...")
            _seed_data(session)
            session.commit()
            print("Database seeding complete.")

def _seed_data(session):
    """Populates the database with some initial sample data."""
    customers_data = [
        {"id": "c1", "name": "Alice Smith", "phone": "+15551234567", "email": "alice@example.com", "status": "Contactado"},
        {"id": "c2", "name": "Bob Johnson", "phone": "+15557654321", "email": "bob@example.com", "status": "Interesado"},
        {"id": "c3", "name": "Charlie Brown", "phone": "+15558675309", "email": "charlie@example.com", "status": "Nuevo"},
    ]
    session.execute(customers_table.insert(), customers_data)

    products_data = [
        {"id": "p1", "name": "Servicio de Consultoría", "price": 150.0},
        {"id": "p2", "name": "Soporte Técnico Mensual", "price": 75.0},
        {"id": "p3", "name": "Desarrollo Web Básico", "price": 800.0},
    ]
    session.execute(products_table.insert(), products_data)

    scheduled_posts_data = [
        {
            "id": "sp1",
            "date": datetime.date.today() + datetime.timedelta(days=2),
            "content_type": "text",
            "content_data_json": json.dumps({"content": "Este es un post de texto de prueba programado."})
        }
    ]
    session.execute(scheduled_posts_table.insert(), scheduled_posts_data)

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database ready.")
