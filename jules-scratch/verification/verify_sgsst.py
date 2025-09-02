# jules-scratch/verification/verify_sgsst.py
import re
import datetime
from playwright.sync_api import sync_playwright, Page, expect

def run_test(page: Page):
    """
    Tests the SG-SST agent by sending a command and verifying the response.
    """
    print("Navigating to the SG-SST application...")
    page.goto("http://127.0.0.1:8551", timeout=60000)

    # Wait for the main view to load
    expect(page.get_by_text("Incidentes")).to_be_visible(timeout=30000)
    print("Application loaded. Navigating to AI Assistant...")

    # Click on the AI Assistant navigation rail item
    ai_assistant_button = page.get_by_text("Asistente IA")
    expect(ai_assistant_button).to_be_visible()
    ai_assistant_button.click()

    # Wait for the agent's initial message
    expect(page.get_by_text("Hola, soy el General de SG-SST.")).to_be_visible(timeout=30000)
    print("AI Assistant view loaded. Finding chat input...")

    # Find the input field and send a command
    chat_input = page.get_by_label("Escribe tu orden de SG-SST aquí...")
    expect(chat_input).to_be_visible()
    print("Chat input found. Sending command...")

    today_str = datetime.date.today().isoformat()
    command = f"Quiero reportar un incidente. El empleado 'EMP-001' se resbaló en la 'Bodega Principal'. La descripción es 'Piso mojado sin señalización'. La fecha fue {today_str}."
    chat_input.fill(command)

    # Click the send button
    send_button = page.get_by_tooltip("Enviar Orden")
    expect(send_button).to_be_enabled()
    send_button.click()
    print("Command sent. Waiting for agent response...")

    # Wait for the agent's final response
    final_response_locator = page.locator(".ft-text", has_text=re.compile(r"Successfully reported incident"))

    expect(final_response_locator).to_be_visible(timeout=60000)
    print("Agent response received.")

    # Take a screenshot for visual verification
    screenshot_path = "jules-scratch/verification/sgsst_test.png"
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
            page.screenshot(path="jules-scratch/verification/sgsst_test_error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
