print("auth_routes.py LOADED")

import os
import logging
from fastapi import APIRouter, HTTPException
from models import User
import database
from datetime import datetime
import utils.auth_utils as auth_utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Loaded auth_routes from:", os.path.abspath(__file__))
print("auth_utils loaded, SECRET_KEY =", auth_utils.SECRET_KEY, "| type:", type(auth_utils.SECRET_KEY))

auth_router = APIRouter()


@auth_router.post("/signup")
def signup(user: User):
    try:
        logger.info("/signup endpoint called")

        database.connect_to_mongo()
        if database.users_collection is None:
            raise Exception("users_collection is None (DB connection failed)")

        existing_user = database.users_collection.find_one({"email": user.email})
        if existing_user:
            logger.warning(f"⚠️ Signup failed: {user.email} already registered")
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pw = auth_utils.hash_password(user.password)
        database.users_collection.insert_one({
            "email": user.email,
            "password": hashed_pw,
            "created_at": datetime.utcnow()
        })

        logger.info(f"User {user.email} registered successfully")
        return {"message": "User registered successfully"}

    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")


@auth_router.post("/login")
def login(user: User):
    try:
        logger.info("⚡ /login endpoint called")
        logger.info(f"⚡ Using SECRET_KEY = {auth_utils.SECRET_KEY} | type: {type(auth_utils.SECRET_KEY)}")

        database.connect_to_mongo()
        if database.users_collection is None:
            raise Exception("users_collection is None (DB connection failed)")

        db_user = database.users_collection.find_one({"email": user.email})
        if not db_user:
            logger.warning(f"Login failed: no user found with {user.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not auth_utils.verify_password(user.password, db_user["password"]):
            logger.warning(f"Login failed: wrong password for {user.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = auth_utils.create_access_token({"sub": user.email})
        logger.info(f"Token created successfully for {user.email}")

        return {
            "access_token": token,
            "token_type": "bearer",
            "message": "Login successful"
        }

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
