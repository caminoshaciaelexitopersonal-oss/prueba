import flet as ft
import threading
import time
from agent.graph import SgsstAgent
import database

class RiskView(ft.UserControl):
    def __init__(self, agent: SgsstAgent):
        super().__init__(expand=True)
        self.agent = agent

        self.risk_list = ft.ListView(expand=True, spacing=10)
        self.refresh_button = ft.ElevatedButton("Refresh List", on_click=self.refresh_risk_list)

        self.chat_input = ft.TextField(
            hint_text="e.g., 'add risk named Fall Hazard in Warehouse area...'",
            expand=True,
            on_submit=self.send_message_click,
        )
        self.send_button = ft.IconButton(icon=ft.icons.SEND, on_click=self.send_message_click)

        self.chat_history = ft.ListView(expand=True, spacing=10, auto_scroll=True)

        self.refresh_risk_list(None)

    def build(self):
        return ft.Column(
            controls=[
                ft.Row([ft.Text("Risk Management Matrix", size=24, weight=ft.FontWeight.BOLD), self.refresh_button]),
                ft.Text("Use the chat below to manage risks with the AI agent."),
                ft.Divider(),
                ft.Container(
                    content=self.risk_list,
                    border=ft.border.all(1, ft.Colors.BLACK26),
                    border_radius=ft.border_radius.all(5),
                    padding=ft.padding.all(10),
                    expand=4,
                ),
                ft.Divider(),
                ft.Container(
                    content=self.chat_history,
                    border=ft.border.all(1, ft.Colors.BLACK26),
                    border_radius=ft.border_radius.all(5),
                    padding=ft.padding.all(10),
                    expand=2,
                ),
                ft.Row(
                    controls=[self.chat_input, self.send_button],
                ),
            ],
            expand=True,
        )

    def refresh_risk_list(self, e):
        self.risk_list.controls.clear()
        risks = database.list_risks()
        if not risks:
            self.risk_list.controls.append(ft.Text("No risks found."))
        else:
            for risk in risks:
                self.risk_list.controls.append(
                    ft.Text(f"[{risk.area}] {risk.name} (Level: {risk.risk_level})")
                )
        self.update()

    def send_message_click(self, e):
        user_input = self.chat_input.value
        if not user_input:
            return

        self.add_to_chat_history("You", user_input)
        self.chat_input.value = ""
        self.update()

        thread = threading.Thread(target=self.run_agent, args=(user_input,))
        thread.start()

    def run_agent(self, prompt):
        agent_response_text = ft.Text("Agent is thinking...")
        self.page.run_threadsafe(self.add_control_to_chat, ("Agent", agent_response_text))

        response_content = ""
        try:
            for chunk in self.agent.invoke(prompt):
                last_message = chunk['messages'][-1]
                if last_message.content:
                    response_content = last_message.content
                self.page.run_threadsafe(self.update_agent_response, (agent_response_text, response_content))
                time.sleep(0.1)
        except Exception as e:
            self.page.run_threadsafe(self.update_agent_response, (agent_response_text, f"An error occurred: {e}"))

    def add_to_chat_history(self, user, message):
        self.chat_history.controls.append(
            ft.Row([ft.Text(f"{user}: ", weight=ft.FontWeight.BOLD), ft.Text(message, selectable=True)])
        )
        self.update()

    def add_control_to_chat(self, user, control):
        self.chat_history.controls.append(
             ft.Row([ft.Text(f"{user}: ", weight=ft.FontWeight.BOLD), control])
        )
        self.update()

    def update_agent_response(self, text_control, new_content):
        text_control.value = new_content
        self.update()
