import flet as ft
from .oportunidades_y_pipeline.teniente import TenienteOportunidadesYPipeline

class CapitanOportunidadesYPipeline:
    def __init__(self, page: ft.Page):
        self.page = page
        self.teniente = TenienteOportunidadesYPipeline(page=self.page)
        print("Capitán de Oportunidades y Pipeline: En servicio.")

    def ejecutar_mision(self, mision: str) -> str:
        """
        Recibe una misión del general y la delega al teniente.
        La 'mision' es una cadena que contiene la operación a realizar.
        Ej: "command='add', customer_id='some-uuid', source='website'"
        """
        print(f"Capitán (Pipeline): Misión recibida - '{mision}'.")
        print("Capitán: Delegando operación al equipo táctico.")

        resultado_tactico = self.teniente.ejecutar_operacion(mision)

        print("Capitán: Reporte táctico recibido.")
        return f"Capitán: Misión completada. {resultado_tactico}"
