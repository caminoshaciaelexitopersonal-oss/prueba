import flet as ft
from .. import database

class RiskView(ft.Column):
    def __init__(self):
        super().__init__(expand=True)
        self.risk_list = ft.ListView(expand=True, spacing=10)

    def did_mount(self):
        """Called after the control is added to the page."""
        # Subscribe to the 'risk_update' topic.
        # The handler (self.on_risk_update) will be called when a message is received.
        self.page.pubsub.subscribe(self.on_risk_update)
        self.refresh_risk_list()

    def will_unmount(self):
        """Called before the control is removed from the page."""
        self.page.pubsub.unsubscribe(self.on_risk_update)
        super().will_unmount()

    def on_risk_update(self, message):
        """Handler for Pub/Sub messages."""
        # When a message is received on the 'risk_update' topic, refresh the list.
        self.refresh_risk_list()

    def build(self):
        """Builds the UI for the RiskView."""
        return ft.Column(
            controls=[
                ft.Row([ft.Text("Matriz de Riesgos (IPERC)", size=24, weight=ft.FontWeight.BOLD)]),
                ft.Text("La lista de riesgos se actualiza en tiempo real basada en las acciones del agente."),
                ft.Divider(),
                ft.Container(
                    content=self.risk_list,
                    border=ft.border.all(1, ft.colors.BLACK26),
                    border_radius=ft.border_radius.all(5),
                    padding=ft.padding.all(10),
                    expand=True,
                ),
            ],
            expand=True,
        )

    def refresh_risk_list(self):
        """Fetches risks from the database and updates the ListView."""
        self.risk_list.controls.clear()
        try:
            risks = database.list_risks()
            if not risks:
                self.risk_list.controls.append(ft.Text("No hay riesgos registrados."))
            else:
                for risk in risks:
                    self.risk_list.controls.append(
                        ft.Text(f"[{risk.area}] {risk.name} (Nivel: {risk.risk_level})")
                    )
        except Exception as e:
            self.risk_list.controls.append(ft.Text(f"Error al cargar riesgos: {e}", color=ft.colors.RED))

        # This needs to be called to update the UI
        if self.page:
            self.update()
