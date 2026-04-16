import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)

def send_welcome_email(email: str, full_name: str):
    """
    Envía un correo electrónico de bienvenida al usuario.
    Si el servidor SMTP no está configurado, el mensaje se registra únicamente en los logs (modo depuración).
    """
    subject = f"¡Bienvenido a SERVICED, {full_name}!"
    body = f"""
    Hola {full_name},
    
    ¡Gracias por unirte a SERVICED! Estamos muy contentos de tenerte con nosotros.
    
    Explora nuestra plataforma para encontrar los mejores servicios o para ofrecer los tuyos.
    
    Si tienes alguna pregunta, no dudes en contactarnos.
    
    Saludos,
    El equipo de SERVICED
    """

    # Verifica la configuración de SMTP
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
        logger.warning(f"SMTP no configurado. El correo de bienvenida para {email} se registró en el log.")
        print(f"\n--- [DEBUG EMAIL] PARA: {email} ---")
        print(f"Asunto: {subject}")
        print(f"Contenido: {body}")
        print("--- [FIN DEBUG EMAIL] ---\n")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            
        logger.info(f"Correo de bienvenida enviado a {email}")
    except Exception as e:
        logger.error(f"Error enviando correo de bienvenida a {email}: {e}")

def send_password_reset_email(email: str, token: str):
    """
    Envía un correo electrónico con un enlace para restablecer la contraseña.
    """
    subject = "Restablece tu contraseña - SERVICED"
    # El enlace apunta al frontend para que el usuario gestione el cambio
    reset_link = f"{settings.FRONTEND_HOST}/users/reset-password.html?token={token}"
    body = f"""
    Hola,
    
    Has solicitado restablecer tu contraseña en SERVICED. Haz clic en el siguiente enlace para continuar:
    
    {reset_link}
    
    Si no solicitaste este cambio, puedes ignorar este correo.
    
    Saludos,
    El equipo de SERVICED
    """

    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
        logger.warning(f"SMTP no configurado. El correo de restablecimiento para {email} se registró en el log.")
        print(f"\n--- [DEBUG EMAIL] PARA: {email} ---")
        print(f"Asunto: {subject}")
        print(f"Contenido: {body}")
        print("--- [FIN DEBUG EMAIL] ---\n")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            
        logger.info(f"Correo de restablecimiento enviado a {email}")
    except Exception as e:
        logger.error(f"Error enviando correo de restablecimiento a {email}: {e}")

class EmailService:
    @staticmethod
    def send_welcome_email(email: str, full_name: str):
        return send_welcome_email(email, full_name)
    
    @staticmethod
    def send_password_reset_email(email: str, token: str):
        return send_password_reset_email(email, token)

email_service = EmailService()
