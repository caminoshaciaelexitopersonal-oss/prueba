import flet as ft
from .soldado import SoldadoOportunidadesYPipeline

class SargentoOportunidadesYPipeline:
    def __init__(self, page: ft.Page):
        self.page = page
        self.soldado = SoldadoOportunidadesYPipeline(page=self.page)
        print("Sargento de Oportunidades y Pipeline: Listo para la acción.")

    def ejecutar_tarea(self, tarea: str) -> str:
        """
        Recibe una tarea del teniente y la convierte en una acción para el soldado.
        """
        print(f"Sargento (Pipeline): Tarea recibida - '{tarea}'.")

        # La tarea es la acción directa para el soldado en este caso.
        accion_soldado = tarea

        print(f"Sargento: Dando orden final al soldado: '{accion_soldado}'")
        resultado_soldado = self.soldado.ejecutar_accion(accion_soldado)

        print("Sargento: Reporte del soldado recibido.")
        return f"Sargento: Tarea completada. {resultado_soldado}"
