# activos_fijos/agents/corps/general_activos.py
import os
from dotenv import load_dotenv
from activos_fijos.agents.corps.units.capitan_activos import ActivosCaptain

# Cargar variables de entorno
load_dotenv()

class GeneralActivos:
    """
    El 'General de Activos Fijos' es el punto de entrada para todas las
    órdenes de alto nivel relacionadas con la gestión de activos.
    Delega las tareas al 'Capitán de Activos'.
    """
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la variable de entorno OPENAI_API_KEY.")

        self.capitan_activos = ActivosCaptain(api_key=api_key)

    def process_command(self, query: str) -> str:
        """
        Procesa un comando de lenguaje natural del usuario.
        Delega la tarea directamente al Capitán de Activos.
        """
        print(f"General de Activos: Orden recibida - '{query}'. Delegando al Capitán.")

        response = self.capitan_activos.run(query)

        print(f"General de Activos: Misión completada. Respuesta final: {response}")
        return response

# Ejemplo de uso
if __name__ == '__main__':
    general = GeneralActivos()

    comando_usuario = "Registra una nueva computadora para el área de diseño. Costó 5.000.000, la compramos hoy, tiene un valor residual de 200.000 y una vida útil de 36 meses. El método es línea recta. La cuenta de activo es la 152805, la de depreciación acumulada es 159205, el gasto es 516010 y pagamos desde bancos (111005)."

    resultado_final = general.process_command(comando_usuario)
    print(f"\n--- Fin de la Simulación ---\nRespuesta del Agente: {resultado_final}")
