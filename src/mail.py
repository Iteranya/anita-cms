# email_utils.py
import resend
from src.config import load_or_create_mail_config


def send_contact_email(name: str, company: str, email: str, phone: str, service: str, message: str):
    mail_config = load_or_create_mail_config()
    resend.api_key = mail_config.api_key
    html_content = f"""
    <h2>Pesan Baru dari Form Kontak</h2>
    <ul>
        <li><strong>Nama:</strong> {name}</li>
        <li><strong>Perusahaan:</strong> {company}</li>
        <li><strong>Email:</strong> {email}</li>
        <li><strong>Telepon:</strong> {phone}</li>
        <li><strong>Layanan:</strong> {service}</li>
    </ul>
    <p><strong>Pesan:</strong><br>{message}</p>
    """

    response = resend.Emails.send({
        "from": mail_config.server_email,  # Replace with your verified domain email
        "to": [mail_config.target_email],
        "subject": f"[Kontak] {name} - {company}",
        "html": html_content
    })

    return response
