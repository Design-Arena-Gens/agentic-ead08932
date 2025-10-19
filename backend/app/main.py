from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

leads_db = {}
emails_db = {}
scheduler = BackgroundScheduler()

class Lead(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    company: Optional[str] = None
    phone: Optional[str] = None
    status: str = "new"
    created_at: Optional[datetime] = None
    last_contacted: Optional[datetime] = None

class EmailOutreach(BaseModel):
    id: Optional[str] = None
    lead_id: str
    subject: str
    body: str
    sent_at: Optional[datetime] = None
    responded: bool = False
    scheduled_call: Optional[datetime] = None

class ChatMessage(BaseModel):
    message: str
    lead_id: Optional[str] = None

class CallSchedule(BaseModel):
    lead_id: str
    scheduled_time: datetime
    phone: str

def check_and_schedule_calls():
    current_time = datetime.now()
    for email_id, email in emails_db.items():
        if not email["responded"] and email["sent_at"]:
            time_since_sent = current_time - email["sent_at"]
            if time_since_sent >= timedelta(days=1) and not email.get("scheduled_call"):
                lead = leads_db.get(email["lead_id"])
                if lead and lead.get("phone"):
                    email["scheduled_call"] = current_time + timedelta(minutes=5)
                    lead["status"] = "call_scheduled"
                    print(f"Scheduled call for lead {lead['name']} at {email['scheduled_call']}")

@app.on_event("startup")
async def startup_event():
    scheduler.add_job(check_and_schedule_calls, 'interval', minutes=5)
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/leads")
async def create_lead(lead: Lead):
    lead_id = str(uuid.uuid4())
    lead_data = lead.model_dump()
    lead_data["id"] = lead_id
    lead_data["created_at"] = datetime.now()
    leads_db[lead_id] = lead_data
    return lead_data

@app.get("/api/leads")
async def get_leads():
    return list(leads_db.values())

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str):
    if lead_id not in leads_db:
        raise HTTPException(status_code=404, detail="Lead not found")
    return leads_db[lead_id]

@app.put("/api/leads/{lead_id}")
async def update_lead(lead_id: str, lead: Lead):
    if lead_id not in leads_db:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead_data = lead.model_dump()
    lead_data["id"] = lead_id
    lead_data["created_at"] = leads_db[lead_id]["created_at"]
    leads_db[lead_id] = lead_data
    return lead_data

@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: str):
    if lead_id not in leads_db:
        raise HTTPException(status_code=404, detail="Lead not found")
    del leads_db[lead_id]
    return {"message": "Lead deleted"}

@app.post("/api/emails")
async def send_email(email: EmailOutreach):
    if email.lead_id not in leads_db:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    email_id = str(uuid.uuid4())
    email_data = email.model_dump()
    email_data["id"] = email_id
    email_data["sent_at"] = datetime.now()
    email_data["responded"] = False
    emails_db[email_id] = email_data
    
    leads_db[email.lead_id]["status"] = "contacted"
    leads_db[email.lead_id]["last_contacted"] = datetime.now()
    
    return email_data

@app.get("/api/emails")
async def get_emails():
    return list(emails_db.values())

@app.get("/api/emails/lead/{lead_id}")
async def get_lead_emails(lead_id: str):
    lead_emails = [email for email in emails_db.values() if email["lead_id"] == lead_id]
    return lead_emails

@app.put("/api/emails/{email_id}/responded")
async def mark_email_responded(email_id: str):
    if email_id not in emails_db:
        raise HTTPException(status_code=404, detail="Email not found")
    emails_db[email_id]["responded"] = True
    lead_id = emails_db[email_id]["lead_id"]
    leads_db[lead_id]["status"] = "responded"
    return emails_db[email_id]

@app.post("/api/chat")
async def chat(message: ChatMessage):
    user_message = message.message.lower()
    
    if "add lead" in user_message or "create lead" in user_message:
        return {
            "response": "I can help you add a new lead. Please provide the lead's name, email, company, and phone number.",
            "action": "create_lead"
        }
    elif "send email" in user_message or "cold email" in user_message:
        if message.lead_id:
            return {
                "response": f"I'll help you send a cold email to this lead. What would you like the subject and message to be?",
                "action": "send_email",
                "lead_id": message.lead_id
            }
        return {
            "response": "Please select a lead first to send an email.",
            "action": "select_lead"
        }
    elif "schedule call" in user_message or "call" in user_message:
        return {
            "response": "I can schedule a call for you. Which lead would you like to call?",
            "action": "schedule_call"
        }
    elif "status" in user_message or "leads" in user_message:
        total_leads = len(leads_db)
        contacted = sum(1 for lead in leads_db.values() if lead["status"] == "contacted")
        responded = sum(1 for lead in leads_db.values() if lead["status"] == "responded")
        return {
            "response": f"You have {total_leads} total leads. {contacted} have been contacted, and {responded} have responded.",
            "action": "show_stats"
        }
    else:
        return {
            "response": "I'm your outreach assistant. I can help you add leads, send cold emails, track responses, and schedule follow-up calls. What would you like to do?",
            "action": "help"
        }

@app.get("/api/stats")
async def get_stats():
    total_leads = len(leads_db)
    total_emails = len(emails_db)
    responded = sum(1 for email in emails_db.values() if email["responded"])
    scheduled_calls = sum(1 for email in emails_db.values() if email.get("scheduled_call"))
    
    return {
        "total_leads": total_leads,
        "total_emails": total_emails,
        "responded": responded,
        "scheduled_calls": scheduled_calls,
        "response_rate": (responded / total_emails * 100) if total_emails > 0 else 0
    }
