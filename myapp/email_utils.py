import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_smtp(host: str, port: int, sender: str, to: str, subject: str, html_body: str, text_body: str | None = None):
    # Buat pesan multipart dengan alternatif (plain-text & HTML)
    msg = MIMEMultipart('alternative')
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject

    if text_body:
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))

    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    # Koneksi SMTP tanpa TLS/SSL (karena MailHog tidak butuh)
    with smtplib.SMTP(host=host, port=port) as server:
        # Tidak perlu login untuk MailHog
        server.send_message(msg)
