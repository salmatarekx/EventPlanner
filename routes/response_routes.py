print("response_routes.py LOADED")

import os
import logging
from fastapi import APIRouter, HTTPException, Header
from datetime import datetime

import database
from models.event_model.event_model import EventResponse
import utils.auth_utils as auth_utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Loaded response_routes from:", os.path.abspath(__file__))

response_router = APIRouter()


def get_current_user(Authorization: str = Header(None)):
    """
    Extract and validate JWT token to get current user email.
    Raises HTTPException if authentication fails.
    """
    try:
        if not Authorization:
            logger.warning("Missing Authorization header")
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        if not Authorization.startswith("Bearer "):
            logger.warning("Invalid Authorization header format")
            raise HTTPException(status_code=401, detail="Invalid Authorization header format. Use 'Bearer <token>'")

        token = Authorization.replace("Bearer ", "").strip()
        
        if not token:
            logger.warning("Empty token provided")
            raise HTTPException(status_code=401, detail="Token is required")

        payload = auth_utils.jwt.decode(token, auth_utils.SECRET_KEY, algorithms=["HS256"])
        user_email = payload.get("sub")

        if not user_email:
            logger.warning("Token payload missing 'sub' field")
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return user_email

    except auth_utils.jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except auth_utils.jwt.JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication error")


def _get_events_collection():
    """
    Get the events collection from database.
    Raises HTTPException if database connection fails.
    """
    try:
        database.connect_to_mongo()
        if database.events_collection is None:
            logger.error("Events collection not initialized")
            raise HTTPException(status_code=500, detail="Database connection failed. Please try again later.")
        return database.events_collection
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection error")


def _validate_event_id(event_id: str):
    """
    Validate and convert event_id string to integer.
    Raises HTTPException if event_id is invalid.
    """
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
        logger.warning(f"Invalid event ID format: {event_id}")
        raise HTTPException(status_code=400, detail="Invalid event ID format. Event ID must be an integer.")


def _get_event_by_id(events_collection, event_id: str):
    """
    Retrieve event by ID.
    Raises HTTPException if event not found.
    """
    try:
        event_id_int = _validate_event_id(event_id)
        event = events_collection.find_one({"_id": event_id_int})
        
        if not event:
            logger.warning(f"Event not found: {event_id}")
            raise HTTPException(status_code=404, detail="Event not found")
        
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving event: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving event")


@response_router.post("/{event_id}/respond")
def respond_to_event(event_id: str, response: EventResponse, Authorization: str = Header(None)):
    """
    Attendees can indicate their attendance status for events (Going, Maybe, Not Going).
    
    - **event_id**: The ID of the event to respond to
    - **response**: The attendance response (Going, Maybe, Not Going)
    
    Returns success message with the recorded response.
    """
    try:
        logger.info(f"POST /events/{event_id}/respond endpoint called")
        
        # Validate authentication
        user_email = get_current_user(Authorization)
        
        # Validate response data
        if not response or not response.response:
            raise HTTPException(status_code=400, detail="Response is required")
        
        valid_responses = ["Going", "Maybe", "Not Going"]
        if response.response not in valid_responses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid response. Must be one of: {', '.join(valid_responses)}"
            )
        
        # Get database collection
        events_collection = _get_events_collection()
        
        # Retrieve event
        event = _get_event_by_id(events_collection, event_id)
        
        # Validate user is an attendee
        attendees = event.get("attendees", [])
        if not attendees:
            logger.warning(f"Event {event_id} has no attendees")
            raise HTTPException(status_code=500, detail="Event has no attendees")
        
        # Find user in attendees list
        attendee_index = -1
        user_role = None
        
        for idx, attendee in enumerate(attendees):
            if attendee.get("email") == user_email:
                user_role = attendee.get("role", "attendee")
                attendee_index = idx
                break
        
        # Check if user is organizer
        if user_role == "organizer":
            logger.info(f"Organizer {user_email} attempted to respond to event {event_id}")
            raise HTTPException(
                status_code=400, 
                detail="Organizers do not need to respond. They are automatically marked as attending."
            )
        
        # Check if user is an attendee
        if attendee_index == -1:
            logger.warning(f"User {user_email} is not an attendee of event {event_id}")
            raise HTTPException(
                status_code=403, 
                detail="You are not an attendee of this event. Please request an invitation first."
            )
        
        # Update the attendee's response status
        try:
            attendees[attendee_index]["response"] = response.response
            attendees[attendee_index]["response_updated_at"] = datetime.utcnow()
            
            event_id_int = _validate_event_id(event_id)
            update_result = events_collection.update_one(
                {"_id": event_id_int},
                {"$set": {"attendees": attendees}}
            )
            
            if update_result.matched_count == 0:
                logger.error(f"Event {event_id} not found during update")
                raise HTTPException(status_code=404, detail="Event not found")
            
            if update_result.modified_count == 0:
                logger.warning(f"No changes made to event {event_id} - response may be the same")
            
            logger.info(f"User {user_email} set response '{response.response}' for event {event_id}")
            return {
                "message": f"Response '{response.response}' recorded successfully",
                "event_id": event_id,
                "response": response.response,
                "updated_at": attendees[attendee_index]["response_updated_at"].isoformat() if isinstance(attendees[attendee_index]["response_updated_at"], datetime) else None
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating response in database: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update response. Please try again.")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in respond_to_event: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")


@response_router.get("/{event_id}/attendees")
def get_event_attendees(event_id: str, Authorization: str = Header(None)):
    """
    Organizers can view the list of attendees and their statuses for each event.
    
    - **event_id**: The ID of the event to get attendees for
    
    Returns detailed list of attendees with their response statuses and summary statistics.
    """
    try:
        logger.info(f"GET /events/{event_id}/attendees endpoint called")
        
        # Validate authentication
        user_email = get_current_user(Authorization)
        
        # Get database collection
        events_collection = _get_events_collection()
        
        # Retrieve event
        event = _get_event_by_id(events_collection, event_id)
        
        # Validate user is the organizer
        organizer_email = event.get("organizer")
        if not organizer_email:
            logger.error(f"Event {event_id} has no organizer")
            raise HTTPException(status_code=500, detail="Event data is corrupted: missing organizer")
        
        if organizer_email != user_email:
            logger.warning(f"User {user_email} attempted to view attendees for event {event_id} (not organizer)")
            raise HTTPException(
                status_code=403, 
                detail="Only the event organizer can view attendee responses"
            )
        
        # Build attendees list with response statuses
        attendees_list = []
        attendees_data = event.get("attendees", [])
        
        if not attendees_data:
            logger.info(f"Event {event_id} has no attendees")
            return {
                "event_id": event_id,
                "event_title": event.get("title", "Unknown"),
                "attendees": [],
                "total_attendees": 0,
                "response_summary": {
                    "Going": 0,
                    "Maybe": 0,
                    "Not Going": 0,
                    "No Response": 0
                }
            }
        
        for attendee in attendees_data:
            try:
                attendee_email = attendee.get("email")
                if not attendee_email:
                    logger.warning(f"Attendee entry missing email in event {event_id}")
                    continue
                
                attendee_info = {
                    "email": attendee_email,
                    "role": attendee.get("role", "attendee"),
                    "response": attendee.get("response", "No Response"),
                    "response_updated_at": attendee.get("response_updated_at")
                }
                
                # Format datetime if present
                if attendee_info["response_updated_at"] and isinstance(attendee_info["response_updated_at"], datetime):
                    attendee_info["response_updated_at"] = attendee_info["response_updated_at"].isoformat()
                
                attendees_list.append(attendee_info)
            except Exception as e:
                logger.warning(f"Error processing attendee entry: {str(e)}")
                continue
        
        # Calculate response summary
        response_summary = {
            "Going": sum(1 for a in attendees_list if a.get("response") == "Going"),
            "Maybe": sum(1 for a in attendees_list if a.get("response") == "Maybe"),
            "Not Going": sum(1 for a in attendees_list if a.get("response") == "Not Going"),
            "No Response": sum(1 for a in attendees_list if a.get("response") == "No Response")
        }
        
        logger.info(f"Retrieved {len(attendees_list)} attendees for event {event_id}")
        return {
            "event_id": event_id,
            "event_title": event.get("title", "Unknown"),
            "attendees": attendees_list,
            "total_attendees": len(attendees_list),
            "response_summary": response_summary
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_event_attendees: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")

