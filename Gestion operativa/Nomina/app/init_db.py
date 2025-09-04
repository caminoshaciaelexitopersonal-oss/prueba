from database import engine, Base
from models import Employee, Contract

def main():
    print("Inicializando la base de datos de Nómina...")
    print("Creando todas las tablas definidas en los modelos...")

    # La siguiente línea crea las tablas en la base de datos
    # si no existen.
    Base.metadata.create_all(bind=engine)

    print("¡Base de datos de Nómina inicializada exitosamente!")
    print("Tablas 'employees' y 'contracts' creadas.")

if __name__ == "__main__":
    main()
