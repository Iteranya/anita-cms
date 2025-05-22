# email_utils.py
import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY", "re_your_key_here")  # Use dotenv or environment variables

def send_contact_email(name: str, company: str, email: str, phone: str, service: str, message: str):
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
        "from": "onboarding@resend.dev",  # Replace with your verified domain email
        "to": ["yourmail@gmail.com"],
        "subject": f"[Kontak] {name} - {company}",
        "html": html_content
    })

    return response
