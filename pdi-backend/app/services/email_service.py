import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_evaluation_notification(
    to_email: str, 
    recipient_name: str, 
    evaluation_type: str,
    employee_name: str
):
    host = os.getenv("MAIL_HOST")
    port = int(os.getenv("MAIL_PORT"))
    username = os.getenv("MAIL_USERNAME")
    password = os.getenv("MAIL_PASSWORD")
    mail_from = os.getenv("MAIL_FROM")
    
    if not host or not username or not password:
        print("[EMAIL WARNING] Credenciais de e-mail não configuradas. Disparo ignorado.")
        return
    
    msg = MIMEMultipart("alternative")
    msg["From"] = mail_from
    msg["To"] = to_email
    
    if evaluation_type == "SELF":
        msg["Subject"] = "Autoavaliação de Desempenho está disponível"
        html_content = f"""
        <h2>Olá {recipient_name}!</h2>
        <p>O seu formulário de <strong>Autoavaliação</strong> está disponível.</p>
        <p>Acesse a plataforma para preencher sua avaliação de desempenho.</p>
        """
        
    elif evaluation_type == "MANAGER":
        msg["Subject"] = f"Avaliação de Desempenho de {employee_name} está disponível"
        html_content = f"""
        <h2>Olá {recipient_name}!</h2>
        <p>O formulário de avaliação de desempenho do colaborador <strong>{employee_name}</strong> está disponível.</p>
        <p>Acesse a plataforma para preencher sua avaliação.</p>
        """
    msg.attach(MIMEText(html_content, "html"))
    
    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(mail_from, to_email, msg.as_string())
        print(f"[EMAIL] Notificação enviada para {to_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] Falha ao enviar e-mail para {to_email}: {e}")