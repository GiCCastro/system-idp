import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_evaluation_notification(
    to_email: str, 
    recipient_name: str, 
    evaluation_type: str,
    employee_name: str,
    cycle: str = "",
    evaluation_id: int | None = None,
    user_id: int | None = None
):
    host = os.getenv("MAIL_HOST")
    port = int(os.getenv("MAIL_PORT") or 587)
    username = os.getenv("MAIL_USERNAME")
    password = os.getenv("MAIL_PASSWORD")
    mail_from = os.getenv("MAIL_FROM")
    frontend_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:4200").rstrip("/")
    
    if not host or not username or not password:
        print("[EMAIL WARNING] Credenciais de e-mail não configuradas. Disparo ignorado.")
        return

    if user_id and evaluation_id:
        evaluation_link = f"{frontend_url}/avaliacoes?userId={user_id}&evaluationId={evaluation_id}"
    else:
        evaluation_link = f"{frontend_url}/avaliacoes"

    cycle_label = f" (Ciclo {cycle})" if cycle else ""
    
    msg = MIMEMultipart("alternative")
    msg["From"] = mail_from
    msg["To"] = to_email
    
    if evaluation_type == "SELF":
        msg["Subject"] = f"Autoavaliação de Desempenho disponível{cycle_label}"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; color: #1F2426; line-height: 1.6; max-width: 560px;">
            <h2 style="color: #184A57; margin-bottom: 8px;">Olá, {recipient_name}!</h2>
            <p>O seu formulário de <strong>Autoavaliação (SELF)</strong> referente ao ciclo <strong>{cycle}</strong> já está disponível para preenchimento.</p>
            <p style="margin: 24px 0;">
                <a href="{evaluation_link}"
                   style="background-color: #184A57; color: #FFFFFF; padding: 10px 18px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                    Acessar Minha Autoavaliação
                </a>
            </p>
            <p style="font-size: 12px; color: #4E5559;">
                Ou copie e cole este link no navegador:<br>
                <a href="{evaluation_link}" style="color: #184A57;">{evaluation_link}</a>
            </p>
        </div>
        """
        
    elif evaluation_type == "MANAGER":
        msg["Subject"] = f"Avaliação de Desempenho de {employee_name} disponível{cycle_label}"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; color: #1F2426; line-height: 1.6; max-width: 560px;">
            <h2 style="color: #184A57; margin-bottom: 8px;">Olá, {recipient_name}!</h2>
            <p>O formulário de <strong>Avaliação do Gestor (MANAGER)</strong> do(a) colaborador(a) <strong>{employee_name}</strong> referente ao ciclo <strong>{cycle}</strong> já está disponível.</p>
            <p style="margin: 24px 0;">
                <a href="{evaluation_link}"
                   style="background-color: #184A57; color: #FFFFFF; padding: 10px 18px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                    Acessar Avaliação do Colaborador
                </a>
            </p>
            <p style="font-size: 12px; color: #4E5559;">
                Ou copie e cole este link no navegador:<br>
                <a href="{evaluation_link}" style="color: #184A57;">{evaluation_link}</a>
            </p>
        </div>
        """
    msg.attach(MIMEText(html_content, "html"))

    # No plano gratuito do Mailtrap Sandbox existe limite de taxa por segundo (Rate Limit).
    # O segundo e-mail (MANAGER) aguarda um pequeno intervalo e possui retry automático.
    if evaluation_type == "MANAGER":
        time.sleep(2.0)

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(username, password)
                server.sendmail(mail_from, to_email, msg.as_string())
            print(f"[EMAIL] Notificação enviada para {to_email} ({evaluation_type} - Ciclo {cycle})")
            return
        except Exception as e:
            if attempt < max_attempts:
                print(f"[EMAIL RETRY {attempt}/{max_attempts}] Aguardando limite do servidor SMTP para enviar para {to_email}... ({e})")
                time.sleep(3.0 * attempt)
            else:
                print(f"[EMAIL ERROR] Falha ao enviar e-mail para {to_email}: {e}")
