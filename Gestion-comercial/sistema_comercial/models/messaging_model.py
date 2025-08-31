from typing import List
# We need the Customer dataclass to know what a recipient is
from models.sales_model import Customer

class MessagingModel:
    def __init__(self):
        pass

    def prepare_message_summary(self, channel: str, subject: str, body: str, recipients: List[Customer]) -> str:
        """
        Prepares a summary of the message to be sent for confirmation dialogs.
        """
        recipient_names = ", ".join([r.name for r in recipients])
        if len(recipient_names) > 100:
            recipient_names = recipient_names[:100] + "..."

        summary = (
            f"Canal: {channel}\n"
            f"Destinatarios ({len(recipients)}): {recipient_names}\n"
            f"Asunto: {subject if subject else 'N/A'}"
        )
        return summary

    def simulate_send(self, channel: str, subject: str, body: str, recipients: List[Customer]):
        """
        Simulates the sending process by printing to the console.
        This will be replaced by actual API calls later.

        -------------------------------------------------------------------
        PARA HABILITAR ENVÍOS REALES - INSTRUCCIONES:
        -------------------------------------------------------------------
        1. Instala las librerías necesarias desde tu terminal:
           pip install sendgrid twilio

        2. Añade las claves de API correspondientes a tu archivo .env:
           SENDGRID_API_KEY='SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
           TWILIO_ACCOUNT_SID='ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
           TWILIO_AUTH_TOKEN='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
           TWILIO_PHONE_NUMBER='+15017122661' # Tu número de Twilio
           FROM_EMAIL='tu_email_verificado@example.com' # Tu email verificado en SendGrid

        3. Descomenta el código de ejemplo de abajo y reemplaza la lógica
           de simulación con este bloque.
        -------------------------------------------------------------------
        """
        # --- LÓGICA DE SIMULACIÓN (reemplazar con el código real de abajo) ---
        print("="*50)
        print("INICIANDO SIMULACIÓN DE ENVÍO MASIVO")
        print(f"Canal: {channel}, Destinatarios: {len(recipients)}")
        print("="*50)
        for recipient in recipients:
            contact_info = recipient.email if channel == 'Email' else recipient.phone
            print(f"  -> Simulando envío a {recipient.name} ({contact_info})...")
        print("="*50)
        print("SIMULACIÓN FINALIZADA")
        print("="*50)

        # --- EJEMPLO DE CÓDIGO REAL (descomentar y adaptar) ---
        # import os
        # from sendgrid import SendGridAPIClient
        # from sendgrid.helpers.mail import Mail
        # from twilio.rest import Client
        #
        # if channel == "Email":
        #     try:
        #         sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        #         from_email = os.environ.get('FROM_EMAIL')
        #         for recipient in recipients:
        #             message = Mail(from_email=from_email, to_emails=recipient.email, subject=subject, html_content=body)
        #             sg.send(message)
        #             print(f"Email enviado a {recipient.name}")
        #     except Exception as e:
        #         print(f"Error enviando emails: {e}")
        #
        # elif channel == "SMS" or channel == "WhatsApp":
        #     try:
        #         client = Client(os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))
        #         from_number = os.environ.get('TWILIO_PHONE_NUMBER')
        #         prefix = "whatsapp:" if channel == "WhatsApp" else ""
        #
        #         for recipient in recipients:
        #             to_number = f"{prefix}{recipient.phone}"
        #             from_full_number = f"{prefix}{from_number}"
        #             message = client.messages.create(body=body, from_=from_full_number, to=to_number)
        #             print(f"{channel} enviado a {recipient.name}, SID: {message.sid}")
        #     except Exception as e:
        #         print(f"Error enviando {channel}: {e}")
