# jules-scratch/verification/verify_contabilidad.py
import re
from playwright.sync_api import sync_playwright, Page, expect

def run_test(page: Page):
    """
    Tests the Contabilidad agent by sending a command and verifying the response.
    """
    print("Navigating to the application...")
    page.goto("http://127.0.0.1:8550", timeout=60000)

    # Wait for the initial bot message to ensure the view is loaded
    expect(page.get_by_text("Hola, soy el General Contable.")).to_be_visible(timeout=30000)
    print("Application loaded. Finding chat input...")

    # Find the input field and send a command
    chat_input = page.get_by_label("Escribe tu orden aquí...")
    expect(chat_input).to_be_visible()
    print("Chat input found. Sending command...")

    command = "Necesito registrar una compra de suministros de oficina por 150.000 pesos. Pagamos de contado desde la caja general."
    chat_input.fill(command)

    # Click the send button
    send_button = page.get_by_tooltip("Enviar mensaje")
    expect(send_button).to_be_enabled()
    send_button.click()
    print("Command sent. Waiting for agent response...")

    # Wait for the agent's final response
    # The response should contain the success message
    final_response_locator = page.locator(".ft-text", has_text=re.compile(r"Éxito: Comprobante registrado con el ID \d+"))

    expect(final_response_locator).to_be_visible(timeout=60000) # Increased timeout for agent processing
    print("Agent response received.")

    # Take a screenshot for visual verification
    screenshot_path = "jules-scratch/verification/contabilidad_test.png"
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            run_test(page)
        except Exception as e:
            print(f"An error occurred during Playwright test: {e}")
            page.screenshot(path="jules-scratch/verification/contabilidad_test_error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
