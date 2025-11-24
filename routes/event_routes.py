print("event_routes.py LOADED")

import os
import logging
from fastapi import APIRouter, HTTPException, Header
from datetime import datetime
from bson import ObjectId

import database
from models.event_model.event_model import EventCreate, InviteUser
import utils.auth_utils as auth_utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Loaded event_routes from:", os.path.abspath(__file__))

event_router = APIRouter()

def get_current_user(Authorization: str = Header(None)):
    try:
        if not Authorization:
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        token = Authorization.replace("Bearer ", "").strip()
        payload = auth_utils.jwt.decode(token, auth_utils.SECRET_KEY, algorithms=["HS256"])

        return payload.get("sub")

    except Exception as e:
        logger.error(f"Token decode error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


def _get_events_collection():
    database.connect_to_mongo()
    if database.events_collection is None:
        raise HTTPException(status_code=500, detail="Events collection not initialized")
    return database.events_collection


def _serialize_event(event_doc, user_email: str):

    event_copy = {**event_doc}
    event_copy["id"] = str(event_copy.pop("_id"))

    user_role = "attendee"
    if event_copy.get("organizer") == user_email:
        user_role = "organizer"
    else:
        for attendee in event_copy.get("attendees", []):
            if attendee.get("email") == user_email:
                user_role = attendee.get("role", "attendee")
                break

    event_copy["user_role"] = user_role
    event_copy["is_organizer"] = event_copy.get("organizer") == user_email
    return event_copy

@event_router.post("/create")
def create_event(event: EventCreate, Authorization: str = Header(None)):
    try:
        logger.info("/events/create endpoint called")
        user_email = get_current_user(Authorization)

        events_collection = _get_events_collection()

        new_event = {
            "title": event.title,
            "description": event.description,
            "date": event.date,
            "time": event.time,
            "location": event.location,
            "organizer": user_email,
            "attendees": [
                {"email": user_email, "role": "organizer"}
            ],
            "created_at": datetime.utcnow()
        }

        result = events_collection.insert_one(new_event)

        logger.info(f"Event created by {user_email}: {str(result.inserted_id)}")
        return {"message": "Event created successfully", "event_id": str(result.inserted_id)}

    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@event_router.get("/my-events")
def get_my_events(Authorization: str = Header(None)):
    try:
        logger.info("/events/my-events endpoint called")
        user_email = get_current_user(Authorization)

        events_collection = _get_events_collection()
        events = [
            _serialize_event(ev, user_email)
            for ev in events_collection.find({"organizer": user_email})
        ]

        return events

    except Exception as e:
        logger.error(f"Error fetching my events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
@event_router.get("/me")
def get_all_user_events(Authorization: str = Header(None)):
    try:
        logger.info("/events/me endpoint called")
        user_email = get_current_user(Authorization)

        events_collection = _get_events_collection()
        events = [
            _serialize_event(ev, user_email)
            for ev in events_collection.find({
                "$or": [
                    {"organizer": user_email},
                    {"attendees.email": user_email}
                ]
            })
        ]

        return events

    except Exception as e:
        logger.error(f"Error fetching events for user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")


@event_router.get("/invited")
def get_invited_events(Authorization: str = Header(None)):
    try:
        logger.info("/events/invited endpoint called")
        user_email = get_current_user(Authorization)

        events_collection = _get_events_collection()
        events = [
            _serialize_event(ev, user_email)
            for ev in events_collection.find({
                "attendees": {
                    "$elemMatch": {
                        "email": user_email,
                        "role": "attendee"
                    }
                }
            })
        ]

        return events

    except Exception as e:
        logger.error(f"Error fetching invited events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")


@event_router.post("/invite")
def invite_user(invite: InviteUser, Authorization: str = Header(None)):
    try:
        logger.info("/events/invite endpoint called")
        user_email = get_current_user(Authorization)

        events_collection = _get_events_collection()

        try:
            event_id = ObjectId(invite.event_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid event ID format")

        event = events_collection.find_one({"_id": event_id})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if event["organizer"] != user_email:
            raise HTTPException(status_code=403, detail="Only the organizer can invite users")

        # Prevent duplicate invites
        for attendee in event["attendees"]:
            if attendee["email"] == invite.email:
                raise HTTPException(status_code=400, detail="User already invited")

        events_collection.update_one(
            {"_id": event_id},
            {"$push": {"attendees": {"email": invite.email, "role": "attendee"}}}
        )

        logger.info(f"User {invite.email} invited to event {invite.event_id}")
        return {"message": "User invited successfully"}

    except Exception as e:
        logger.error(f"Error inviting user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@event_router.delete("/{event_id}")
def delete_event(event_id: str, Authorization: str = Header(None)):
    try:
        logger.info("/events/delete endpoint called")
        user_email = get_current_user(Authorization)

        events_collection = _get_events_collection()

        try:
            event_object_id = ObjectId(event_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid event ID format")

        event = events_collection.find_one({"_id": event_object_id})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if event["organizer"] != user_email:
            raise HTTPException(status_code=403, detail="Only organizer can delete event")

        events_collection.delete_one({"_id": event_object_id})

        logger.info(f"Event deleted by {user_email}: {event_id}")
        return {"message": "Event deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
