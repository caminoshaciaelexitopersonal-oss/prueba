# gestion_operativa/SG-SST/agents/corps/general_sgsst.py
import os
from dotenv import load_dotenv
from gestion_operativa.SG_SST.agents.corps.units.capitan_sgsst import SGSSTCaptain

# Cargar variables de entorno
load_dotenv()

class GeneralSGSST:
    """
    El 'General de SG-SST' es el punto de entrada para todas las
    órdenes de alto nivel relacionadas con la gestión de seguridad y salud.
    """
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la variable de entorno OPENAI_API_KEY.")

        self.capitan_sgsst = SGSSTCaptain(api_key=api_key)

    def process_command(self, query: str) -> str:
        """
        Procesa un comando de lenguaje natural del usuario.
        Delega la tarea directamente al Capitán de SG-SST.
        """
        print(f"General de SG-SST: Orden recibida - '{query}'. Delegando al Capitán.")

        response = self.capitan_sgsst.run(query)

        print(f"General de SG-SST: Misión completada. Respuesta final: {response}")
        return response
