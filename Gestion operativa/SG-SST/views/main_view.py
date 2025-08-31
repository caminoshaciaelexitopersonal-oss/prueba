import flet as ft
from .incident_view import IncidentView
from .risk_view import RiskView
from agent.graph import SgsstAgent

class MainView(ft.UserControl):
    def __init__(self):
        super().__init__(expand=True)

        self.agent = SgsstAgent()
        self.incident_view = IncidentView(agent=self.agent)
        self.risk_view = RiskView(agent=self.agent)

        self.navigation_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.WARNING_AMBER,
                    selected_icon=ft.icons.WARNING,
                    label="Incidents",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SHIELD_OUTLINED,
                    selected_icon=ft.icons.SHIELD,
                    label="Risks",
                ),
            ],
            on_change=self.nav_change,
        )

        self.content_area = ft.Container(
            content=self.incident_view,
            expand=True,
            padding=ft.padding.all(20),
        )

    def build(self):
        return ft.Row(
            controls=[
                self.navigation_rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
            expand=True,
        )

    def nav_change(self, e):
        index = e.control.selected_index
        if index == 0:
            self.content_area.content = self.incident_view
        elif index == 1:
            self.content_area.content = self.risk_view
        self.update()
