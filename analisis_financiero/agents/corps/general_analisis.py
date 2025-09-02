# analisis_financiero/agents/corps/general_analisis.py
import os
from dotenv import load_dotenv
from analisis_financiero.agents.corps.units.capitan_analisis import AnalisisCaptain

# Cargar variables de entorno
load_dotenv()

class GeneralAnalisis:
    """
    El 'General de Análisis Financiero' es el punto de entrada para todas las
    órdenes de alto nivel relacionadas con la generación de ratios y análisis.
    """
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la variable de entorno OPENAI_API_KEY.")

        self.capitan_analisis = AnalisisCaptain(api_key=api_key)

    def process_command(self, query: str) -> str:
        """
        Procesa un comando de lenguaje natural del usuario.
        Delega la tarea directamente al Capitán de Análisis.
        """
        print(f"General de Análisis: Orden recibida - '{query}'. Delegando al Capitán.")

        response = self.capitan_analisis.run(query)

        print(f"General de Análisis: Misión completada. Respuesta final: {response}")
        return response

# Ejemplo de uso
if __name__ == '__main__':
    general = GeneralAnalisis()

    comando_usuario = "genérame el análisis financiero completo para la fecha 2023-12-31"

    resultado_final = general.process_command(comando_usuario)
    print(f"\n--- Fin de la Simulación ---\nRespuesta del Agente: {resultado_final}")
