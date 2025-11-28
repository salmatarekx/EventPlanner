print("event_routes.py LOADED")

import os
import logging
from fastapi import APIRouter, HTTPException, Header
from datetime import datetime

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


def _get_next_event_id():
    database.connect_to_mongo()
    if database.counters_collection is None:
        raise HTTPException(status_code=500, detail="Counters collection not initialized")
    
    result = database.counters_collection.find_one_and_update(
        {"_id": "event_id"},
        {"$inc": {"sequence_value": 1}},
        return_document=True
    )
    
    if result is None:
        database.counters_collection.insert_one({"_id": "event_id", "sequence_value": 1})
        return 1
    
    return result["sequence_value"]


def _validate_event_id(event_id: str):
    if not event_id or not isinstance(event_id, str):
        raise HTTPException(status_code=400, detail="Event ID is required and must be a string")
    
    if len(event_id.strip()) == 0:
        raise HTTPException(status_code=400, detail="Event ID cannot be empty")
    
    try:
        event_id_int = int(event_id)
        if event_id_int < 1:
            raise HTTPException(status_code=400, detail="Event ID must be a positive integer starting from 1")
        return event_id_int
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid event ID format. Event ID must be an integer.")


def _serialize_event(event_doc, user_email: str):
    event_copy = {**event_doc}
    
    if "_id" in event_copy:
        event_copy["id"] = event_copy.pop("_id")
    elif "id" not in event_copy:
        event_copy["id"] = event_copy.get("event_id")

    user_role = "attendee"
    user_response = None
    if event_copy.get("organizer") == user_email:
        user_role = "organizer"
    else:
        for attendee in event_copy.get("attendees", []):
            if attendee.get("email") == user_email:
                user_role = attendee.get("role", "attendee")
                user_response = attendee.get("response")
                break

    event_copy["user_role"] = user_role
    event_copy["is_organizer"] = event_copy.get("organizer") == user_email
    event_copy["user_response"] = user_response
    
    if event_copy.get("attendees"):
        for attendee in event_copy["attendees"]:
            if attendee.get("email") == user_email:
                attendee["my_response"] = attendee.get("response")
                break
    
    return event_copy

@event_router.post("/create")
def create_event(event: EventCreate, Authorization: str = Header(None)):
    try:
        logger.info("/events/create endpoint called")
        user_email = get_current_user(Authorization)

        events_collection = _get_events_collection()
        
        event_id = _get_next_event_id()

        new_event = {
            "_id": event_id,
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

        events_collection.insert_one(new_event)

        logger.info(f"Event created by {user_email}: {event_id}")
        return {"message": "Event created successfully", "event_id": event_id}

    except HTTPException:
        raise
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

        logger.info(f"User {user_email} retrieved {len(events)} organized events")
        return events

    except HTTPException:
        raise
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

        logger.info(f"User {user_email} retrieved {len(events)} total events")
        return events

    except HTTPException:
        raise
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

        logger.info(f"User {user_email} retrieved {len(events)} invited events")
        return events

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching invited events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")


@event_router.post("/invite")
def invite_user(invite: InviteUser, Authorization: str = Header(None)):
    try:
        logger.info("/events/invite endpoint called")
        user_email = get_current_user(Authorization)

        events_collection = _get_events_collection()

        event_id = _validate_event_id(invite.event_id)

        event = events_collection.find_one({"_id": event_id})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if event.get("organizer") != user_email:
            logger.warning(f"User {user_email} attempted to invite to event {event_id} (not organizer)")
            raise HTTPException(
                status_code=403, 
                detail="Only the event organizer can invite users to this event"
            )

        for attendee in event.get("attendees", []):
            if attendee.get("email") == invite.email:
                raise HTTPException(status_code=400, detail="User already invited to this event")

        database.connect_to_mongo()
        if database.users_collection is None:
            raise HTTPException(status_code=500, detail="Users collection not initialized")
        
        existing_user = database.users_collection.find_one({"email": invite.email})
        if not existing_user:
            logger.warning(f"Invite failed: email {invite.email} does not exist in the system")
            raise HTTPException(
                status_code=404, 
                detail="User with this email does not exist. Please invite only registered users."
            )

        events_collection.update_one(
            {"_id": event_id},
            {"$push": {"attendees": {"email": invite.email, "role": "attendee"}}}
        )

        logger.info(f"User {invite.email} invited to event {event_id} by organizer {user_email}")
        return {"message": "User invited successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inviting user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@event_router.delete("/{event_id}")
def delete_event(event_id: str, Authorization: str = Header(None)):
    try:
        logger.info(f"/events/delete endpoint called for event {event_id}")
        user_email = get_current_user(Authorization)

        events_collection = _get_events_collection()

        event_id_int = _validate_event_id(event_id)

        event = events_collection.find_one({"_id": event_id_int})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        organizer_email = event.get("organizer")
        if organizer_email != user_email:
            logger.warning(f"User {user_email} attempted to delete event {event_id} created by {organizer_email}")
            raise HTTPException(
                status_code=403, 
                detail="You cannot delete this event. Only the event creator can delete it."
            )

        delete_result = events_collection.delete_one({"_id": event_id_int})
        
        if delete_result.deleted_count == 0:
            logger.error(f"Failed to delete event {event_id}")
            raise HTTPException(status_code=500, detail="Failed to delete event")

        logger.info(f"Event {event_id} deleted by creator {user_email}")
        return {"message": "Event deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
