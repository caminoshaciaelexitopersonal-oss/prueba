# gestion_operativa/Nomina/agents/corps/general_nomina.py
import os
from dotenv import load_dotenv
from gestion_operativa.Nomina.agents.corps.units.capitan_nomina import NominaCaptain

# Cargar variables de entorno
load_dotenv()

class GeneralNomina:
    """
    El 'General de Nómina' es el punto de entrada para todas las
    órdenes de alto nivel relacionadas con la gestión de la nómina.
    """
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la variable de entorno OPENAI_API_KEY.")

        self.capitan_nomina = NominaCaptain(api_key=api_key)

    def process_command(self, query: str) -> str:
        """
        Procesa un comando de lenguaje natural del usuario.
        Delega la tarea directamente al Capitán de Nómina.
        """
        print(f"General de Nómina: Orden recibida - '{query}'. Delegando al Capitán.")

        response = self.capitan_nomina.run(query)

        print(f"General de Nómina: Misión completada. Respuesta final: {response}")
        return response
