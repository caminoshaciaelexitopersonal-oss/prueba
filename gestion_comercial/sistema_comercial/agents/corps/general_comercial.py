# gestion_comercial/sistema_comercial/agents/corps/general_comercial.py
import os
from dotenv import load_dotenv
from gestion_comercial.sistema_comercial.agents.corps.units.capitan_ventas import VentasCaptain

# Cargar variables de entorno
load_dotenv()

class GeneralComercial:
    """
    El 'General Comercial' es el punto de entrada para todas las
    órdenes de alto nivel relacionadas con la gestión comercial y de ventas.
    """
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la variable de entorno OPENAI_API_KEY.")

        self.capitan_ventas = VentasCaptain(api_key=api_key)

    def process_command(self, query: str) -> str:
        """
        Procesa un comando de lenguaje natural del usuario.
        Delega la tarea directamente al Capitán de Ventas.
        """
        print(f"General Comercial: Orden recibida - '{query}'. Delegando al Capitán de Ventas.")

        response = self.capitan_ventas.run(query)

        print(f"General Comercial: Misión completada. Respuesta final: {response}")
        return response
