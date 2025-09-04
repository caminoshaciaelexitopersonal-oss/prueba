import flet as ft
# Note: We will create sargento.py in the next step, so this import will resolve then.
from .sargento import SargentoRegistroPerfil360

class TenienteRegistroPerfil360:
    def __init__(self, page: ft.Page):
        self.page = page
        self.sargento = SargentoRegistroPerfil360(page=self.page)
        print("Teniente de Registro y Perfil 360: A la orden.")

    def ejecutar_operacion(self, operacion: str) -> str:
        """
        Recibe una operación del capitán y la delega al sargento.
        """
        print(f"Teniente (Registro y Perfil): Operación recibida - '{operacion}'.")
        print("Teniente: Pasando tarea al sargento.")

        resultado_sargento = self.sargento.ejecutar_tarea(operacion)

        print("Teniente: Reporte del sargento recibido.")
        return f"Teniente: Operación completada. {resultado_sargento}"
