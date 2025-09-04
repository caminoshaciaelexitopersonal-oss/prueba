import flet as ft
from .registro_y_perfil_360.teniente import TenienteRegistroPerfil360

class CapitanRegistroPerfil360:
    def __init__(self, page: ft.Page):
        self.page = page
        self.teniente = TenienteRegistroPerfil360(page=self.page)
        print("Capitán de Registro y Perfil 360: En servicio.")

    def ejecutar_mision(self, mision: str) -> str:
        """
        Recibe una misión del general y la delega al teniente.
        La 'mision' es una cadena que contiene la operación a realizar.
        Ej: "command='add', name='Jane Doe', email='jane.doe@email.com', phone='987654321'"
        """
        print(f"Capitán (Registro y Perfil): Misión recibida - '{mision}'.")
        print("Capitán: Delegando operación al equipo táctico.")

        resultado_tactico = self.teniente.ejecutar_operacion(mision)

        print("Capitán: Reporte táctico recibido.")
        return f"Capitán: Misión completada. {resultado_tactico}"
