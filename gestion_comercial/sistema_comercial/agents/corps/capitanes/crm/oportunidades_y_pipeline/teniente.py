import flet as ft
from .sargento import SargentoOportunidadesYPipeline

class TenienteOportunidadesYPipeline:
    def __init__(self, page: ft.Page):
        self.page = page
        self.sargento = SargentoOportunidadesYPipeline(page=self.page)
        print("Teniente de Oportunidades y Pipeline: A la orden.")

    def ejecutar_operacion(self, operacion: str) -> str:
        """
        Recibe una operación del capitán y la delega al sargento.
        """
        print(f"Teniente (Pipeline): Operación recibida - '{operacion}'.")
        print("Teniente: Pasando tarea al sargento.")

        resultado_sargento = self.sargento.ejecutar_tarea(operacion)

        print("Teniente: Reporte del sargento recibido.")
        return f"Teniente: Operación completada. {resultado_sargento}"
