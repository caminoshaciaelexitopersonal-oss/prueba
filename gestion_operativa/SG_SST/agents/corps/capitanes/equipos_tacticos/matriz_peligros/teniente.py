import flet as ft
from .sargento import SargentoMatrizPeligros

class TenienteMatrizPeligros:
    def __init__(self, page: ft.Page):
        self.page = page
        # Pasar 'page' al siguiente en la cadena
        self.sargento = SargentoMatrizPeligros(page=self.page)
        print("Teniente de Matriz de Peligros: A la orden.")

    def ejecutar_operacion(self, operacion: str):
        print(f"Teniente: Operación recibida - '{operacion}'.")
        print("Teniente: Asignando tareas al sargento.")
        # La tarea para el sargento podría ser más estructurada en el futuro
        resultado_sargento = self.sargento.ejecutar_tarea(
            "Añadir riesgo: 'Caída de objetos', Área: 'Almacén', Nivel: 'Alto'"
        )
        print(f"Teniente: Reporte recibido del sargento.")
        return f"Teniente: Operación completada. {resultado_sargento}"
