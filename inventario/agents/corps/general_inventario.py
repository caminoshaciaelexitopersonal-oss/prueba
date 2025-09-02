# inventario/agents/corps/general_inventario.py
import os
from dotenv import load_dotenv
from inventario.agents.corps.units.capitan_inventario import InventarioCaptain

# Cargar variables de entorno
load_dotenv()

class InventarioGeneral:
    """
    El 'General de Inventario' es el punto de entrada para todas las
    órdenes de alto nivel relacionadas con la gestión de inventario.
    Delega las tareas al 'Capitán de Inventario'.
    """
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la variable de entorno OPENAI_API_KEY.")

        # El General tiene a su 'Capitán de Inventario' bajo su mando.
        self.capitan_inventario = InventarioCaptain(api_key=api_key)

    def process_command(self, query: str) -> str:
        """
        Procesa un comando de lenguaje natural del usuario.
        Delega la tarea directamente al Capitán de Inventario.
        """
        print(f"General de Inventario: Orden recibida - '{query}'. Delegando al Capitán.")

        response = self.capitan_inventario.run(query)

        print(f"General de Inventario: Misión completada. Respuesta final: {response}")
        return response

# Ejemplo de uso (para pruebas directas)
if __name__ == '__main__':
    general = InventarioGeneral()

    # comando_usuario = "Crea un nuevo producto con nombre 'Teclado Mecánico', SKU 'TEC-MEC-01', descripción 'Teclado para gaming', costo de 85.00 y 15 unidades iniciales."
    comando_usuario = "Registra una compra de 10 unidades del producto con ID 1 a un costo de 90.00 cada una."

    resultado_final = general.process_command(comando_usuario)
    print(f"\n--- Fin de la Simulación ---\nRespuesta del Agente: {resultado_final}")
