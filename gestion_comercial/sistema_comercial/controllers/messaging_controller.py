import flet as ft
from models.messaging_model import MessagingModel
from models.sales_model import SalesModel
from views.messaging_view import MessagingView

class MessagingController:
    def __init__(self, msg_model: MessagingModel, sales_model: SalesModel, view: MessagingView, page: ft.Page):
        self.msg_model = msg_model
        self.sales_model = sales_model
        self.view = view
        self.page = page

        # Connect handlers
        self.view.channel_tabs.on_change = self.on_channel_change
        self.view.select_all_checkbox.on_change = self.toggle_all_recipients
        self.view.send_button.on_click = self.confirm_send

        # Initial setup
        self.populate_recipients()
        self.on_channel_change()

    def populate_recipients(self):
        """Loads customers from the sales model into the recipient list."""
        customers = self.sales_model.get_customers()
        self.view.recipients_list.controls.clear()
        for customer in customers:
            cb = ft.Checkbox(label=f"{customer.name}", data=customer)
            self.view.recipients_list.controls.append(cb)
        self.view.update()

    def on_channel_change(self, e=None):
        """Shows or hides the subject field and updates recipient labels."""
        is_email = (self.view.channel_tabs.selected_index == 0)
        self.view.subject_field.visible = is_email

        for cb in self.view.recipients_list.controls:
            customer = cb.data
            contact_info = ""
            if self.view.channel_tabs.selected_index == 0:
                contact_info = customer.email
            else:
                contact_info = customer.phone
            cb.label = f"{customer.name} ({contact_info})"
        self.view.update()

    def toggle_all_recipients(self, e):
        """Checks or unchecks all recipient checkboxes."""
        for cb in self.view.recipients_list.controls:
            cb.value = e.control.value
        self.view.update()

    def confirm_send(self, e):
        """Shows a confirmation dialog before sending."""
        selected_checkboxes = [cb for cb in self.view.recipients_list.controls if cb.value]
        if not selected_checkboxes:
            self.page.snack_bar = ft.SnackBar(ft.Text("Por favor, selecciona al menos un destinatario."), action="Cerrar")
            self.page.snack_bar.open = True
            self.page.update()
            return

        recipients = [cb.data for cb in selected_checkboxes]
        channel = self.view.channel_tabs.tabs[self.view.channel_tabs.selected_index].text
        subject = self.view.subject_field.value if self.view.subject_field.visible else ""
        body = self.view.body_field.value

        if not body:
            self.page.snack_bar = ft.SnackBar(ft.Text("El cuerpo del mensaje no puede estar vacío."), action="Cerrar")
            self.page.snack_bar.open = True
            self.page.update()
            return

        summary = self.msg_model.prepare_message_summary(channel, subject, body, recipients)

        def on_confirm(e_confirm):
            self.page.dialog.open = False
            self.page.update()
            self.execute_send(channel, subject, body, recipients)

        def on_cancel(e_cancel):
            self.page.dialog.open = False
            self.page.update()

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Envío"),
            content=ft.Text(summary),
            actions=[
                ft.ElevatedButton("Confirmar y Enviar", on_click=on_confirm),
                ft.OutlinedButton("Cancelar", on_click=on_cancel),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def execute_send(self, channel, subject, body, recipients):
        """Calls the model to simulate the send and shows a notification."""
        self.msg_model.simulate_send(channel, subject, body, recipients)
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Simulación de envío de '{channel}' a {len(recipients)} destinatarios completada."), action="Cerrar")
        self.page.snack_bar.open = True
        self.page.update()
