import os
from typing import Optional
from enum import Enum

from fastapi import FastAPI, Form, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import requests

# Load config
load_dotenv("config.env")

app = FastAPI()

# Configs
SF_SALESFORCE_URL = os.getenv("SF_SALESFORCE_URL")
SF_ORG_ID = os.getenv("SF_ORG_ID")
SF_RETURN_URL_SUCCESS = os.getenv("SF_RETURN_URL_SUCCESS")
SF_RETURN_URL_ERROR = os.getenv("SF_RETURN_URL_ERROR")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
APP_DOMAIN = os.getenv("APP_DOMAIN")

# Mappings (from PHP)
FIELD_DISPLAY_NAMES = {
    'first_name': 'Tên',
    'last_name': 'Họ',
    'mobile': 'Điện thoại',
    'email': 'Email',
    'company': 'Công ty',
    'description': 'Ghi chú',
    '00N0o00000M9Lpq': 'SP sẽ chào',
    '00NBV000000Piur': 'Facebook',
    'url': 'Trang web',
    '00NBV000000VDf4': 'Salesman',
    'lead_source': 'Nguồn Lead'
}

PRODUCT_HASHTAGS = {
    'Tay khoan Morita': '#Taykhoan #Morita',
    'Máy Scan Cruxell / XQ Chóp': 'Máy Scan #Cruxell #CRX1000 / XQ Chóp #V080',
    'Nội nha TRZX2, ĐVC': 'Nội nha #TRZX2+, ĐVC',
    'Máy phẫu thuật Siêu âm Mectron': '#MECTRON #PIEZOSURGERY Máy phẫu thuật Siêu âm',
    'Tay rung rửa nội nha EndoUltra': 'Tay rung rửa nội nha #EndoUltra',
    'Pink Wave': 'Đèn trám quang trùng hợp #PinkWave',
    'Máy hút trung tâm': 'Máy hút trung tâm #TCTS2 #TOYKYOGIKEN',
    'Máy CBCT Morita': 'Máy #CBCT #Morita',
    'Máy Pano IC5HD': 'Máy Pano #IC5HD',
    'Ghế nha khoa cao cấp': 'Ghế nha khoa cao cấp #SIGNO',
    'Máy Laser nha khoa': 'Máy #Laser nha khoa',
    'Chất hàn tạm Calcipex II': 'Calci đặt ống tủy #Calcipex II',
    'SmearOFF': 'Dung dịch #VistaApex #SmearOFF',
    'Chlor-XTRA': 'Dung dịch #VistaApex #ChlorXTRA',
    'Vật liệu trám bít ống tủy BG Multi': 'Vật liệu trám bít ống tủy #BGMulti #Nishika',
    'Chất chống nhạy cảm ngà Nanoseal': 'Chất chống nhạy cảm ngà #Nanoseal #Nishika',
    'I do Implant': 'I do Implant #IDO #Implant',
    'Trâm files EndoStar': 'Trâm files #EndoStar',
    'Workshop/Webinar': 'Workshop',
    'Tạo kết nối, tư vấn khác': 'Liên hệ, tư vấn',
    '&#128205;Sếp giao Account': '&#128205;Sếp giao Account'
}

app.mount("/static", StaticFiles(directory="static"), name="static")

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Error: {e}")

@app.post("/submit")
async def submit_form(
    background_tasks: BackgroundTasks,
    full_name: str = Form(...),
    mobile: str = Form(...),
    email: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    product_interest: Optional[str] = Form(None, alias="00N0o00000M9Lpq"),
    facebook: Optional[str] = Form(None, alias="00NBV000000Piur"),
    url: Optional[str] = Form(None),
    salesman: Optional[str] = Form(None, alias="00NBV000000VDf4"),
    lead_source: Optional[str] = Form(None)
):
    # 1. Validation
    if not full_name or not mobile:
        return RedirectResponse(f"{SF_RETURN_URL_ERROR}?code=missing_fields", status_code=303)

    # 2. Logic (Name split)
    name_parts = full_name.strip().split()
    last_name = name_parts.pop() if name_parts else ""
    first_name = " ".join(name_parts)
    
    if not last_name:
         return RedirectResponse(f"{SF_RETURN_URL_ERROR}?code=invalid_name", status_code=303)

    # 3. Prepare Salesforce Data
    sf_data = {
        "oid": SF_ORG_ID,
        "first_name": first_name,
        "last_name": last_name,
        "mobile": mobile,
        "email": email,
        "company": company,
        "description": description,
        "00N0o00000M9Lpq": product_interest, # Product
        "00NBV000000Piur": facebook,
        "url": url,
        "00NBV000000VDf4": salesman,
        "lead_source": lead_source
    }
    
    # 4. Send to Salesforce
    try:
        sf_res = requests.post(SF_SALESFORCE_URL, data=sf_data)
        if sf_res.status_code >= 400:
             print(f"SF Error: {sf_res.text}")
    except Exception as e:
        print(f"Salesforce Connection Error: {e}")
        return RedirectResponse(f"{SF_RETURN_URL_ERROR}?code=sf_error", status_code=303)

    # 5. Prepare Telegram Message
    tg_message = "<b>Thông tin Lead mới #PUSHLEAD:</b>\n\n"
    
    # Order for TG
    fields_order = [
         ('Họ tên', full_name),
         ('Điện thoại', mobile),
         ('Email', email),
         ('Công ty', company),
         ('Salesman', salesman),
         ('SP sẽ chào', PRODUCT_HASHTAGS.get(product_interest, product_interest)),
         ('Ghi chú', description),
         ('Facebook', facebook),
         ('Trang web', url),
         ('Nguồn Lead', lead_source)
    ]
    
    for label, value in fields_order:
        if value:
             tg_message += f"<b>{label}:</b> {value}\n"
             
    background_tasks.add_task(send_telegram, tg_message)

    return RedirectResponse(SF_RETURN_URL_SUCCESS, status_code=303)

@app.get("/")
def index():
    return RedirectResponse("/static/index.html")

