from pydantic import BaseModel, EmailStr
from typing import Literal

class EventCreate(BaseModel):
    title: str
    description: str
    date: str
    time: str
    location: str

class InviteUser(BaseModel):
    event_id: str
    email: EmailStr

class EventResponse(BaseModel):
    response: Literal["Going", "Maybe", "Not Going"]
