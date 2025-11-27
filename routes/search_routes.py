print("search_routes.py LOADED")

import os
import logging
import re
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from datetime import datetime

import database
import utils.auth_utils as auth_utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Loaded search_routes from:", os.path.abspath(__file__))

search_router = APIRouter()


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


def _serialize_event(event_doc, user_email: str):
    """
    Serialize event document for API response.
    Includes user role and response status.
    Uses integer ID instead of ObjectId.
    """
    try:
        event_copy = {**event_doc}
        
        # Use integer ID instead of ObjectId
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
        
        # Include response status in attendees array for the current user
        if event_copy.get("attendees"):
            for attendee in event_copy["attendees"]:
                if attendee.get("email") == user_email:
                    attendee["my_response"] = attendee.get("response")
                    break
        
        return event_copy
    except Exception as e:
        logger.error(f"Error serializing event: {str(e)}")
        # Return basic event info if serialization fails
        event_copy = {**event_doc}
        if "_id" in event_copy:
            event_copy["id"] = event_copy.pop("_id")
        return event_copy


def _validate_date_format(date_str: str, field_name: str):
    """
    Validate date string format (YYYY-MM-DD).
    Raises HTTPException if format is invalid.
    """
    if not date_str or not isinstance(date_str, str):
        raise HTTPException(status_code=400, detail=f"{field_name} must be a string")
    
    date_str = date_str.strip()
    if not date_str:
        raise HTTPException(status_code=400, detail=f"{field_name} cannot be empty")
    
    # Check format YYYY-MM-DD
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(date_pattern, date_str):
        raise HTTPException(
            status_code=400, 
            detail=f"{field_name} must be in YYYY-MM-DD format (e.g., 2024-12-25)"
        )
    
    # Validate actual date
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"{field_name} is not a valid date. Use YYYY-MM-DD format."
        )
    
    return date_str


def _validate_date_range(start_date: Optional[str], end_date: Optional[str]):
    """
    Validate that start_date is before or equal to end_date.
    Raises HTTPException if invalid.
    """
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            if start > end:
                raise HTTPException(
                    status_code=400, 
                    detail="start_date must be before or equal to end_date"
                )
        except ValueError:
            # This shouldn't happen if _validate_date_format was called first
            raise HTTPException(status_code=400, detail="Invalid date format")


def _validate_role(role: Optional[str]):
    """
    Validate role parameter.
    Raises HTTPException if invalid.
    """
    if role is not None:
        role = role.strip().lower() if isinstance(role, str) else role
        valid_roles = ["organizer", "attendee"]
        if role not in valid_roles:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        return role
    return None


def _sanitize_keyword(keyword: str):
    """
    Sanitize keyword input to prevent regex injection.
    Returns sanitized keyword.
    """
    if not keyword:
        return None
    
    # Remove potentially dangerous regex characters or escape them
    # For basic search, we'll use simple regex escaping
    # In production, consider using MongoDB text search instead
    keyword = keyword.strip()
    
    if len(keyword) > 200:
        raise HTTPException(status_code=400, detail="Keyword search term is too long (max 200 characters)")
    
    return keyword


@search_router.get("/search")
def search_events(
    Authorization: str = Header(None),
    keyword: Optional[str] = Query(None, description="Search in event title and description (case-insensitive)"),
    start_date: Optional[str] = Query(None, description="Filter events from this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter events until this date (YYYY-MM-DD)"),
    role: Optional[str] = Query(None, description="Filter by user role: 'organizer' or 'attendee'")
):
    """
    Advanced search API to filter events based on keywords, dates, and user roles.
    By default, shows ALL events. Use role filter to see only events where user has a specific role.
    
    - **keyword**: Search term to match in event title and description (case-insensitive)
    - **start_date**: Filter events from this date onwards (format: YYYY-MM-DD)
    - **end_date**: Filter events up to this date (format: YYYY-MM-DD)
    - **role**: Optional filter by user's role in events ('organizer' or 'attendee'). If not specified, shows all events.
    
    Returns filtered list of events with applied filters metadata.
    """
    try:
        logger.info("/events/search endpoint called")
        
        # Validate authentication
        user_email = get_current_user(Authorization)
        
        # Validate and sanitize inputs
        validated_keyword = None
        if keyword:
            validated_keyword = _sanitize_keyword(keyword)
        
        validated_start_date = None
        if start_date:
            validated_start_date = _validate_date_format(start_date, "start_date")
        
        validated_end_date = None
        if end_date:
            validated_end_date = _validate_date_format(end_date, "end_date")
        
        # Validate date range
        _validate_date_range(validated_start_date, validated_end_date)
        
        # Validate role
        validated_role = _validate_role(role)
        
        # Get database collection
        events_collection = _get_events_collection()
        
        # Build the MongoDB query
        query = {}
        
        # Filter by user role (optional - if specified, filter by user's role in events)
        try:
            if validated_role == "organizer":
                # Show only events where user is the organizer
                query["organizer"] = user_email
            elif validated_role == "attendee":
                # Show only events where user is an attendee (not organizer)
                query["attendees.email"] = user_email
                query["organizer"] = {"$ne": user_email}
            # If no role specified, show ALL events (no user filter)
        except Exception as e:
            logger.error(f"Error building role query: {str(e)}")
            raise HTTPException(status_code=500, detail="Error building search query")
        
        # Filter by keyword (search in title and description)
        if validated_keyword:
            try:
                # Escape special regex characters for safety
                escaped_keyword = re.escape(validated_keyword)
                keyword_query = {
                    "$or": [
                        {"title": {"$regex": escaped_keyword, "$options": "i"}},
                        {"description": {"$regex": escaped_keyword, "$options": "i"}}
                    ]
                }
                
                if "$or" in query:
                    # Combine with existing $or using $and
                    query = {
                        "$and": [
                            query,
                            keyword_query
                        ]
                    }
                else:
                    query.update(keyword_query)
            except Exception as e:
                logger.error(f"Error building keyword query: {str(e)}")
                raise HTTPException(status_code=500, detail="Error processing keyword search")
        
        # Filter by date range
        if validated_start_date or validated_end_date:
            try:
                date_query = {}
                if validated_start_date:
                    date_query["$gte"] = validated_start_date
                if validated_end_date:
                    date_query["$lte"] = validated_end_date
                
                if date_query:
                    query["date"] = date_query
            except Exception as e:
                logger.error(f"Error building date query: {str(e)}")
                raise HTTPException(status_code=500, detail="Error processing date filter")
        
        # Execute query
        try:
            events = list(events_collection.find(query))
        except Exception as e:
            logger.error(f"Error executing database query: {str(e)}")
            raise HTTPException(status_code=500, detail="Error executing search query. Please try again.")
        
        # Serialize events
        serialized_events = []
        for ev in events:
            try:
                serialized_events.append(_serialize_event(ev, user_email))
            except Exception as e:
                logger.warning(f"Error serializing event {ev.get('_id', ev.get('id', 'unknown'))}: {str(e)}")
                # Continue with other events even if one fails
                continue
        
        logger.info(f"Search returned {len(serialized_events)} events for user {user_email}")
        
        return {
            "results": serialized_events,
            "count": len(serialized_events),
            "filters_applied": {
                "keyword": validated_keyword if validated_keyword else None,
                "start_date": validated_start_date,
                "end_date": validated_end_date,
                "role": validated_role
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_events: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during search. Please try again later.")

