import flet as ft

class InvoicingView(ft.UserControl):
    def build(self):
        self.page_title = ft.Text("Facturación de Pedidos", style=ft.TextThemeStyle.HEADLINE_MEDIUM)

        self.orders_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID de Pedido")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Monto Total")),
                ft.DataColumn(ft.Text("Acciones"), numeric=True),
            ],
            rows=[], # To be populated by the controller
            expand=True,
        )

        return ft.Column(
            controls=[
                self.page_title,
                ft.Divider(),
                ft.Text("Pedidos completados y listos para facturar:"),
                ft.Container(
                    content=self.orders_table,
                    expand=True,
                )
            ],
            expand=True,
            spacing=10
        )
