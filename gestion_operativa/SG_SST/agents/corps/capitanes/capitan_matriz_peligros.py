import flet as ft
from .equipos_tacticos.matriz_peligros.teniente import TenienteMatrizPeligros

class CapitanMatrizPeligros:
    def __init__(self, page: ft.Page):
        self.page = page
        # Pasar 'page' al siguiente en la cadena
        self.teniente = TenienteMatrizPeligros(page=self.page)
        print("Capitán de Matriz de Peligros: En servicio y con equipo táctico listo.")

    def ejecutar_mision(self, tarea: str):
        print(f"Capitán de Matriz de Peligros: Tarea recibida - '{tarea}'.")
        print("Capitán: Delegando a mi equipo táctico para la ejecución.")
        resultado_tactico = self.teniente.ejecutar_operacion(tarea)
        print(f"Capitán: Reporte recibido del equipo táctico.")
        return f"Capitán: Misión completada. {resultado_tactico}"
