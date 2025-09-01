import flet as ft
from langchain_core.messages import HumanMessage
from models.sales_model import SalesModel
from views.sales_manager_view import SalesManagerView

class SalesManagerController:
    def __init__(self, model: SalesModel, view: SalesManagerView, page: ft.Page):
        self.model = model
        self.view = view
        self.page = page
        self.agent_executor = self.model.get_agent_executor()

        # Connect handlers
        self.view.send_button.on_click = self.send_message_async
        self.view.user_input.on_submit = self.send_message_async

        # Add initial greeting
        self.add_message_to_chat("Agente", "Hola, soy tu agente de ventas. Puedes pedirme que busque un cliente o actualice su estado.")

    def add_message_to_chat(self, user: str, text: str, is_user: bool = False):
        """Helper to add a message to the chat history view."""
        self.view.chat_history.controls.append(
            ft.Container(
                content=ft.Text(text, selectable=True, color=ft.Colors.WHITE if not is_user else ft.Colors.BLACK),
                bgcolor=ft.Colors.BLUE_GREY_600 if not is_user else ft.Colors.BLUE_100,
                padding=10,
                border_radius=10,
            )
        )
        self.view.update()

    async def send_message_async(self, e):
        """Handles sending a message to the agent and displaying the response."""
        user_text = self.view.user_input.value
        if not user_text:
            return

        self.add_message_to_chat("Tú", user_text, is_user=True)
        self.view.user_input.value = ""
        self.view.progress_ring.visible = True
        self.view.send_button.disabled = True
        self.view.update()

        try:
            config = {"configurable": {"thread_id": "test_thread"}}
            agent_input = {"messages": [HumanMessage(content=user_text)]}

            response_text = ""
            # Using ainvoke for simplicity to get the final result
            final_state = await self.agent_executor.ainvoke(agent_input, config=config)
            agent_response = final_state["messages"][-1]

            if agent_response.tool_calls:
                # If the agent ends with a tool call, we show that for debugging.
                # A more advanced version might parse this into a clearer message.
                response_text = f"Acción realizada: {agent_response.tool_calls[0]['name']}"
            else:
                response_text = agent_response.content

            self.add_message_to_chat("Agente", response_text)

        except Exception as ex:
            # Display error message in chat
            error_message = f"Ha ocurrido un error: {ex}"
            self.add_message_to_chat("Error", error_message)
            # Also print to console for more details
            print(f"Agent execution error: {ex}")

        finally:
            self.view.progress_ring.visible = False
            self.view.send_button.disabled = False
            self.view.update()
