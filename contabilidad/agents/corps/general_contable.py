# contabilidad/agents/corps/general_contable.py
import os
from dotenv import load_dotenv
from contabilidad.agents.corps.units.capitan_asientos import AsientosCaptain

# Cargar variables de entorno (necesario para la API key de OpenAI)
load_dotenv()

class ContabilidadGeneral:
    """
    El 'General Contable' es el punto de entrada principal para todas las
    órdenes de alto nivel relacionadas con la contabilidad.
    Su responsabilidad es interpretar la orden del usuario y delegarla
    al 'Capitán' o unidad especializada correcta.
    """
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la variable de entorno OPENAI_API_KEY. El general no puede operar sin ella.")

        # El General tiene a su 'Capitán de Asientos' bajo su mando.
        # En el futuro, podría tener más capitanes (ej: CapitanDeReportes, CapitanDeImpuestos).
        self.capitan_asientos = AsientosCaptain(api_key=api_key)

    def process_command(self, query: str) -> str:
        """
        Procesa un comando de lenguaje natural del usuario.

        Por ahora, como prueba de concepto, todas las órdenes se asumen
        que son para crear asientos y se delegan directamente al Capitán de Asientos.
        """
        print(f"General: Orden recibida - '{query}'. Delegando al Capitán de Asientos.")

        # Delegar la tarea al capitán apropiado
        response = self.capitan_asientos.run(query)

        print(f"General: Misión completada. Respuesta final: {response}")
        return response

# Ejemplo de uso (para pruebas directas)
if __name__ == '__main__':
    general = ContabilidadGeneral()

    # Ejemplo de una orden compleja que el sistema de agentes debería poder manejar
    comando_usuario = (
        "Necesito registrar una compra de suministros de oficina por 150.000 pesos. "
        "Pagamos de contado desde la caja general. Por favor, usa la fecha de hoy."
    )

    # El general procesa la orden
    resultado_final = general.process_command(comando_usuario)

    # El resultado final debería ser un mensaje de éxito del Capitán.
    # Se pueden añadir verificaciones en la base de datos aquí.
    print("\n--- Fin de la Simulación ---")
