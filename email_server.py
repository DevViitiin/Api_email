import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("email_server")

# ─── Configuração SMTP ────────────────────────────────────────────────────────
SMTP_HOST    = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT    = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER    = os.getenv("SMTP_USER", "")
SMTP_PASS    = os.getenv("SMTP_PASS", "")
FROM_NAME    = os.getenv("FROM_NAME", "MãoDeObra Admin")
PANEL_SECRET = os.getenv("PANEL_SECRET", "")

# ─── Templates HTML ───────────────────────────────────────────────────────────

def _base_template(title: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#0f1117;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:32px 16px;">
        <table width="560" cellpadding="0" cellspacing="0"
               style="background:#161820;border-radius:14px;border:1px solid #1f2230;overflow:hidden;">

          <!-- Cabeçalho -->
          <tr>
            <td style="background:#0d0f16;padding:24px 32px;border-bottom:1px solid #1f2230;">
              <span style="font-size:22px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">
                Mão<span style="color:#3fd68a;">De</span>Obra
              </span>
              <span style="display:block;font-size:11px;color:#4b5068;margin-top:4px;">
                Plataforma de serviços
              </span>
            </td>
          </tr>

          <!-- Conteúdo -->
          <tr>
            <td style="padding:32px;">
              {body_html}
            </td>
          </tr>

          <!-- Rodapé -->
          <tr>
            <td style="background:#0d0f16;padding:20px 32px;border-top:1px solid #1f2230;
                       text-align:center;font-size:11px;color:#4b5068;">
              Este é um e-mail automático — não responda a esta mensagem.<br/>
              © {datetime.now().year} MãoDeObra · Todos os direitos reservados.
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _pill(text: str, color: str, bg: str) -> str:
    return (
        f'<span style="display:inline-block;padding:4px 12px;border-radius:20px;'
        f'background:{bg};color:{color};font-size:12px;font-weight:700;">{text}</span>'
    )


def _info_row(label: str, value: str) -> str:
    return f"""
    <tr>
      <td style="padding:8px 0;color:#8b8fa8;font-size:13px;width:140px;">{label}</td>
      <td style="padding:8px 0;color:#ffffff;font-size:13px;font-weight:600;">{value}</td>
    </tr>"""


# ── Template: Ação punitiva → usuário denunciado ──────────────────────────────
def build_action_email_reported(data: dict) -> tuple[str, str]:
    action = data.get("action_type", "")
    name   = data.get("reported_name", "Usuário")
    aid    = data.get("archive_id", "N/A")

    action_labels = {
        "ban":        ("Banimento Permanente", "#ef4444", "#2d1515"),
        "suspension": ("Suspensão Temporária", "#f59e0b", "#2d2310"),
        "warning":    ("Advertência Formal",   "#f97316", "#2d1a0a"),
    }
    label, color, bg = action_labels.get(action, ("Ação Administrativa", "#8b8fa8", "#1a1c28"))

    # Mensagem principal por tipo de ação
    if action == "ban":
        headline = "Sua conta foi banida permanentemente"
        detail   = (
            "Após análise minuciosa das denúncias recebidas, identificamos violações "
            "graves e reiteradas dos nossos Termos de Uso. Em razão disso, sua conta "
            "foi <strong style='color:#ef4444;'>banida permanentemente</strong> da plataforma. "
            "Contas banidas não podem ser recuperadas e o cadastro com os mesmos dados é proibido."
        )
    elif action == "suspension":
        days     = data.get("duration_days", "?")
        end_date = _fmt_date(data.get("end_date"))
        headline = f"Sua conta foi suspensa por {days} dias"
        detail   = (
            f"Identificamos uma infração aos nossos Termos de Uso. Sua conta ficará "
            f"<strong style='color:#f59e0b;'>suspensa até {end_date}</strong>. "
            "Durante este período o acesso à plataforma estará bloqueado. "
            "Após o prazo, o acesso será restaurado automaticamente."
        )
    else:  # warning
        headline = "Você recebeu uma advertência formal"
        detail   = (
            "Identificamos uma conduta que viola os Termos de Uso da plataforma. "
            "Esta é uma <strong style='color:#f97316;'>advertência formal</strong>. "
            "Reincidências poderão resultar em suspensão ou banimento da conta."
        )

    rows = ""
    if data.get("article_code"):
        rows += _info_row("Artigo violado", f"Art. {data['article_code']}")
    if data.get("motive"):
        rows += _info_row("Motivo", data["motive"])
    if data.get("justification"):
        rows += _info_row("Justificativa", data["justification"])
    rows += _info_row("Protocolo", f'<span style="font-family:monospace;">{aid}</span>')

    body = f"""
      <p style="font-size:16px;font-weight:800;color:#ffffff;margin:0 0 4px;">
        Olá, {name}
      </p>
      <p style="font-size:13px;color:#8b8fa8;margin:0 0 24px;">
        Notificação de ação administrativa · MãoDeObra
      </p>

      <div style="background:{bg};border:1px solid {color}33;border-radius:10px;padding:20px;margin-bottom:24px;">
        {_pill(label, color, bg.replace("0a","20").replace("10","20"))}
        <p style="font-size:15px;font-weight:700;color:{color};margin:12px 0 6px;">{headline}</p>
        <p style="font-size:13px;color:#8b8fa8;line-height:1.6;margin:0;">{detail}</p>
      </div>

      <table width="100%" cellpadding="0" cellspacing="0"
             style="background:#0d0f16;border-radius:8px;padding:4px 16px;margin-bottom:24px;">
        {rows}
      </table>

      <p style="font-size:12px;color:#4b5068;line-height:1.6;margin:0;">
        Se você acredita que esta ação foi tomada por engano, entre em contato com nossa equipe
        de suporte informando o número de protocolo <strong>{aid}</strong>.
      </p>
    """

    subject = f"[MãoDeObra] {label} — Protocolo {aid}"
    return subject, _base_template(label, body)


# ── Template: Arquivamento → usuário denunciado ───────────────────────────────
def build_archive_email_reported(data: dict) -> tuple[str, str]:
    name = data.get("reported_name", "Usuário")
    aid  = data.get("archive_id", "N/A")

    body = f"""
      <p style="font-size:16px;font-weight:800;color:#ffffff;margin:0 0 4px;">
        Olá, {name}
      </p>
      <p style="font-size:13px;color:#8b8fa8;margin:0 0 24px;">
        Informativo de análise · MãoDeObra
      </p>

      <div style="background:#1a1c28;border:1px solid #1f2230;border-radius:10px;
                  padding:20px;margin-bottom:24px;">
        {_pill("Análise Concluída", "#3fd68a", "#1a3328")}
        <p style="font-size:15px;font-weight:700;color:#3fd68a;margin:12px 0 6px;">
          Denúncia encerrada — sem ação necessária
        </p>
        <p style="font-size:13px;color:#8b8fa8;line-height:1.6;margin:0;">
          Nossa equipe analisou as denúncias direcionadas à sua conta e, com base nas
          evidências disponíveis até o momento, <strong style="color:#ffffff;">não foram
          encontradas irregularidades suficientes</strong> para justificar medidas punitivas.
          O caso foi arquivado.
        </p>
      </div>

      <table width="100%" cellpadding="0" cellspacing="0"
             style="background:#0d0f16;border-radius:8px;padding:4px 16px;margin-bottom:24px;">
        {_info_row("Protocolo", f'<span style="font-family:monospace;">{aid}</span>')}
        {_info_row("Data", _fmt_date(datetime.now().isoformat()))}
      </table>

      <p style="font-size:12px;color:#4b5068;line-height:1.6;margin:0;">
        Continue utilizando a plataforma de forma responsável.
        Este número de protocolo serve como comprovante desta análise.
      </p>
    """

    return f"[MãoDeObra] Análise de denúncia encerrada — Protocolo {aid}", \
           _base_template("Análise Concluída", body)


# ── Template: qualquer ação → denunciante ─────────────────────────────────────
def build_reporter_email(data: dict) -> tuple[str, str]:
    name   = data.get("reporter_name", "Usuário")
    action = data.get("action_type", "archive")
    aid    = data.get("archive_id", "N/A")

    if action == "archive":
        status_pill  = _pill("Análise Concluída", "#3fd68a", "#1a3328")
        status_text  = "Sua denúncia foi analisada e <strong style='color:#ffffff;'>encerrada sem ação punitiva</strong>."
        sub_text     = (
            "Com base nas evidências disponíveis, não foi possível confirmar uma violação "
            "grave o suficiente para penalização. Agradecemos por contribuir com a segurança da plataforma."
        )
    else:
        action_labels = {
            "ban":        ("Ação Tomada · Banimento",   "#ef4444"),
            "suspension": ("Ação Tomada · Suspensão",   "#f59e0b"),
            "warning":    ("Ação Tomada · Advertência", "#f97316"),
        }
        lbl, clr = action_labels.get(action, ("Ação Tomada", "#3fd68a"))
        status_pill = _pill(lbl, clr, "#1a1c28")
        status_text = f"Sua denúncia foi revisada e <strong style='color:{clr};'>medidas foram aplicadas</strong>."
        sub_text    = (
            "Por motivos de privacidade não divulgamos os detalhes exatos da ação. "
            "Saiba que sua contribuição ajuda a manter a plataforma segura para todos."
        )

    body = f"""
      <p style="font-size:16px;font-weight:800;color:#ffffff;margin:0 0 4px;">
        Olá, {name}
      </p>
      <p style="font-size:13px;color:#8b8fa8;margin:0 0 24px;">
        Atualização da sua denúncia · MãoDeObra
      </p>

      <div style="background:#1a1c28;border:1px solid #1f2230;border-radius:10px;
                  padding:20px;margin-bottom:24px;">
        {status_pill}
        <p style="font-size:15px;font-weight:700;color:#ffffff;margin:12px 0 6px;">
          Sua denúncia foi processada
        </p>
        <p style="font-size:13px;color:#8b8fa8;line-height:1.6;margin:0 0 10px;">{status_text}</p>
        <p style="font-size:13px;color:#8b8fa8;line-height:1.6;margin:0;">{sub_text}</p>
      </div>

      <table width="100%" cellpadding="0" cellspacing="0"
             style="background:#0d0f16;border-radius:8px;padding:4px 16px;margin-bottom:24px;">
        {_info_row("Protocolo", f'<span style="font-family:monospace;">{aid}</span>')}
        {_info_row("Data", _fmt_date(datetime.now().isoformat()))}
      </table>

      <p style="font-size:12px;color:#4b5068;line-height:1.6;margin:0;">
        Obrigado por ajudar a manter o MãoDeObra seguro.
        Guarde o número de protocolo <strong>{aid}</strong> para referência futura.
      </p>
    """

    return f"[MãoDeObra] Sua denúncia foi processada — Protocolo {aid}", \
           _base_template("Denúncia Processada", body)


# ─── Utilitário de formatação de data ────────────────────────────────────────

def _fmt_date(iso: str | None) -> str:
    if not iso:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y às %H:%M")
    except Exception:
        return iso


# ─── Envio via SMTP ───────────────────────────────────────────────────────────

def send_email(to_email: str, subject: str, html_body: str) -> bool:
    if not SMTP_USER or not SMTP_PASS:
        log.warning("SMTP não configurado — e-mail não enviado para %s", to_email)
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{FROM_NAME} <{SMTP_USER}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.sendmail(SMTP_USER, to_email, msg.as_string())

        log.info("E-mail enviado → %s | %s", to_email, subject)
        return True
    except Exception as exc:
        log.error("Falha ao enviar e-mail para %s: %s", to_email, exc)
        return False


# ─── Rota principal ───────────────────────────────────────────────────────────

@app.route("/send-action-email", methods=["POST"])
def send_action_email():
    # Verificação opcional de segredo compartilhado
    if PANEL_SECRET:
        secret = request.headers.get("X-Panel-Secret", "")
        if secret != PANEL_SECRET:
            return jsonify({"error": "Não autorizado"}), 401

    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Body JSON inválido"}), 400

    action_type    = data.get("action_type", "")
    reported_email = data.get("reported_email")
    reporter_email = data.get("reporter_email")
    results        = {}

    # ── E-mail para o denunciado ──────────────────────────────────────────────
    if reported_email:
        if action_type == "archive":
            subject, html = build_archive_email_reported(data)
        else:
            subject, html = build_action_email_reported(data)
        results["reported"] = send_email(reported_email, subject, html)
    else:
        results["reported"] = None  # sem e-mail cadastrado

    # ── E-mail para o denunciante ─────────────────────────────────────────────
    if reporter_email:
        subject, html = build_reporter_email(data)
        results["reporter"] = send_email(reporter_email, subject, html)
    else:
        results["reporter"] = None

    log.info("send-action-email concluído | archive_id=%s | results=%s",
             data.get("archive_id"), results)

    return jsonify({"success": True, "results": results}), 200


# ─── Health-check ─────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "smtp_configured": bool(SMTP_USER)}), 200


# ─── Entrypoint ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    log.info("Servidor de e-mail iniciado na porta %d", port)
    app.run(host="0.0.0.0", port=port, debug=debug)