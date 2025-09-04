import flet as ft

def main(page: ft.Page):
    page.title = "Sistema de Gestión de Nómina"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(
        ft.Text("Ejército de Agentes de Nómina: Esperando órdenes del General.", size=20)
    )

if __name__ == "__main__":
    ft.app(target=main)
