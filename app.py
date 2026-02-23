import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Carrega .env localmente (não necessário no Render se variáveis estiverem no painel)
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("email_server")

# Configuração SMTP
SMTP_HOST    = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT    = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER    = os.getenv("SMTP_USER")
SMTP_PASS    = os.getenv("SMTP_PASS")
FROM_NAME    = os.getenv("FROM_NAME", "MãoDeObra Admin")
PANEL_SECRET = os.getenv("PANEL_SECRET", "")

if not SMTP_USER or not SMTP_PASS:
    log.warning("SMTP não configurado! Variáveis de ambiente não encontradas.")

# Função de envio de e-mail
def send_email(to_email: str, subject: str, html_body: str) -> bool:
    if not SMTP_USER or not SMTP_PASS:
        log.warning(f"SMTP não configurado — e-mail não enviado para {to_email}")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{FROM_NAME} <{SMTP_USER}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.sendmail(SMTP_USER, to_email, msg.as_string())

        log.info(f"E-mail enviado → {to_email} | {subject}")
        return True
    except Exception as exc:
        log.error(f"Falha ao enviar e-mail para {to_email}: {exc}")
        return False

# Rota principal
@app.route("/send-action-email", methods=["POST"])
def send_action_email():
    if PANEL_SECRET:
        secret = request.headers.get("X-Panel-Secret", "")
        if secret != PANEL_SECRET:
            return jsonify({"error": "Não autorizado"}), 401

    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    results = {}
    reported_email = data.get("reported_email")
    reporter_email = data.get("reporter_email")

    if reported_email:
        results["reported"] = send_email(
            reported_email,
            data.get("subject_reported", "MãoDeObra"),
            data.get("body_reported", "")
        )
    if reporter_email:
        results["reporter"] = send_email(
            reporter_email,
            data.get("subject_reporter", "MãoDeObra"),
            data.get("body_reporter", "")
        )

    return jsonify({"success": True, "results": results}), 200

# Health-check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "smtp_configured": bool(SMTP_USER)}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
