from database import engine, Base
from models import Employee, Inspection

def main():
    print("Inicializando la base de datos...")
    print("Creando todas las tablas definidas en los modelos...")

    # La siguiente línea crea las tablas en la base de datos
    # si no existen.
    Base.metadata.create_all(bind=engine)

    print("¡Base de datos inicializada exitosamente!")
    print("Tablas 'employees' e 'inspections' creadas.")

if __name__ == "__main__":
    main()
