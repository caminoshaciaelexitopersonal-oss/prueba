from database import SessionLocal, engine
from models import Inspection, Employee

def verify_inspections():
    """
    Connects to the database and prints all records from the inspections table.
    """
    db = SessionLocal()
    try:
        print("\n--- Verificando registros en la tabla 'inspections' ---")

        inspections = db.query(Inspection).all()

        if not inspections:
            print("No se encontraron registros en la tabla 'inspections'.")
        else:
            print(f"Se encontraron {len(inspections)} registros:")
            for insp in inspections:
                print(f"  - ID: {insp.id}, Área: {insp.area}, Estado: {insp.status.value}, Fecha: {insp.inspection_date}")

    finally:
        db.close()
        print("--- Verificación terminada. Conexión a la base de datos cerrada. ---\n")

if __name__ == "__main__":
    # A quick check to ensure the tables exist before querying
    # This is not strictly necessary if init_db.py has been run, but it's good practice.
    from database import Base
    Base.metadata.create_all(bind=engine)

    verify_inspections()
