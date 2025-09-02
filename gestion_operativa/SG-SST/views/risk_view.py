# gestion_operativa/SG-SST/views/risk_view.py
import flet as ft
from gestion_operativa.SG_SST import database

class RiskView(ft.UserControl):
    """
    A clean, simple view to display a list of identified workplace risks.
    """
    def __init__(self):
        super().__init__(expand=True)
        self.risk_list = ft.ListView(expand=True, spacing=10)
        self.refresh_button = ft.ElevatedButton("Refrescar Lista", on_click=self.refresh_risk_list)

    def did_mount(self):
        self.refresh_risk_list(None)

    def build(self):
        return ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.Text("Matriz de Riesgos", size=20, weight=ft.FontWeight.BOLD),
                        self.refresh_button
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                ft.Container(
                    content=self.risk_list,
                    border=ft.border.all(1, ft.Colors.BLACK26),
                    border_radius=ft.border_radius.all(5),
                    padding=ft.padding.all(10),
                    expand=True,
                ),
            ],
            expand=True,
        )

    def refresh_risk_list(self, e):
        self.risk_list.controls.clear()
        try:
            risks = database.list_risks()
            if not risks:
                self.risk_list.controls.append(ft.Text("No se han identificado riesgos."))
            else:
                for risk in risks:
                    self.risk_list.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.SHIELD_ROUNDED),
                            title=ft.Text(f"{risk.name} (Nivel: {risk.risk_level})"),
                            subtitle=ft.Text(f"Área: {risk.area}")
                        )
                    )
        except Exception as ex:
            self.risk_list.controls.append(ft.Text(f"Error al cargar riesgos: {ex}"))

        self.update()
