from fastapi import APIRouter, Form
from src.mail import send_contact_email

router = APIRouter()

@router.post("/contact")
async def send_contact(
    name: str = Form(...),
    company: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    service: str = Form(...),
    message: str = Form(...)
):
    try:
        send_contact_email(name, company, email, phone, service, message)
        return {"status": "sent"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}