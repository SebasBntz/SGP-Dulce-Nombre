import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)



def send_password_reset_email(email: str, token: str):
    """
    Envía un correo electrónico con un enlace para restablecer la contraseña.
    """
    subject = "Restablece tu contraseña - Parroquia"
    body = f"""
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; padding: 40px 20px; margin: 0;">
        <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; padding: 40px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center;">
            <div style="width: 60px; height: 60px; background-color: #0d6e4e; color: white; border-radius: 16px; margin: 0 auto 20px; font-size: 30px; line-height: 60px; font-weight: bold;">
                🔐
            </div>
            <h1 style="color: #0f172a; font-size: 24px; margin-bottom: 10px;">Recuperación de Acceso</h1>
            <p style="color: #475569; font-size: 16px; line-height: 1.5; margin-bottom: 25px; text-align: center;">
                Has solicitado restablecer tu contraseña en el Sistema Parroquial. Utiliza el siguiente PIN de seguridad:
            </p>
            <div style="background-color: #f1f5f9; border: 2px dashed #0d6e4e; color: #0d6e4e; font-size: 32px; font-weight: bold; letter-spacing: 8px; padding: 20px; border-radius: 12px; margin-bottom: 25px;">
                {token}
            </div>
            <p style="color: #94a3b8; font-size: 13px; margin-bottom: 30px; text-align: center;">
                Este código expirará en 15 minutos. Si no solicitaste este cambio, ignora este correo de forma segura.
            </p>
            <p style="color: #64748b; font-size: 14px; margin-bottom: 0; text-align: center;">
                Saludos cordiales,<br>
                <strong>Parroquia Dulce Nombre de Jesús</strong>
            </p>
        </div>
    </body>
    </html>
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
        msg.attach(MIMEText(body, 'html'))

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
    def send_password_reset_email(email: str, token: str):
        return send_password_reset_email(email, token)

email_service = EmailService()
