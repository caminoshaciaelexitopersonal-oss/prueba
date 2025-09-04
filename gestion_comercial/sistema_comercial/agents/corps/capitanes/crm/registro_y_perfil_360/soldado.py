import flet as ft
from gestion_comercial.sistema_comercial.agent.tools import add_new_customer, get_customer_details
import json

class SoldadoRegistroPerfil360:
    def __init__(self, page: ft.Page):
        self.page = page
        print("Soldado de Registro y Perfil 360: ¡Listo y dispuesto!")

    def ejecutar_accion(self, accion: str) -> str:
        """
        Ejecuta la acción final: llama a las herramientas para añadir o consultar clientes.
        Ejemplo de 'accion': "command='add', name='John Doe', email='john.doe@email.com', phone='123456789'"
        Ejemplo de 'accion': "command='get', customer_id='some-uuid-string'"
        """
        print(f"Soldado: ¡Ejecutando acción de perfil! - '{accion}'")

        try:
            # Simple parsing logic
            parts = accion.split(", ")
            command_part = parts[0]
            command = command_part.split("=")[1].strip("'")

            args = {}
            for part in parts[1:]:
                key, value = part.split("=")
                args[key.strip()] = value.strip("'")

            if command == 'add':
                resultado = add_new_customer.invoke(args)
            elif command == 'get':
                resultado = get_customer_details.invoke(args)
            else:
                resultado = "Error: Comando desconocido. Use 'add' o 'get'."

            print(f"Soldado: Herramienta de cliente ejecutada.")

            return f"Soldado: ¡Objetivo cumplido! {resultado}"

        except Exception as e:
            error_message = f"Soldado: Falló la misión. Error al procesar la acción '{accion}'. Detalle: {e}"
            print(error_message)
            return error_message
