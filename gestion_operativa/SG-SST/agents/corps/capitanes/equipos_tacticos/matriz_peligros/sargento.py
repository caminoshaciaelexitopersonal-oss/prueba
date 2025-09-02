import flet as ft
from .soldado import SoldadoMatrizPeligros

class SargentoMatrizPeligros:
    def __init__(self, page: ft.Page):
        self.page = page
        # Pasar 'page' al siguiente en la cadena
        self.soldado = SoldadoMatrizPeligros(page=self.page)
        print("Sargento de Matriz de Peligros: Listo para la acción.")

    def ejecutar_tarea(self, tarea: str):
        print(f"Sargento: Tarea recibida - '{tarea}'.")
        print("Sargento: Dando orden final al soldado.")
        # La tarea para el soldado es la acción final y concreta.
        resultado_soldado = self.soldado.ejecutar_accion(tarea)
        print(f"Sargento: Reporte recibido del soldado.")
        return f"Sargento: Tarea completada. {resultado_soldado}"
