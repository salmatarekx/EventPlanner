from pydantic import BaseModel, EmailStr

class EventCreate(BaseModel):
    title: str
    description: str
    date: str
    time: str
    location: str

class InviteUser(BaseModel):
    event_id: str
    email: EmailStr
