from fastapi import APIRouter, HTTPException
from models import User
from database import connect_to_mongo
from utils.auth_utils import hash_password, verify_password, create_access_token
from datetime import datetime

connect_to_mongo()
from database import users_collection

auth_router = APIRouter()

@auth_router.post("/signup")
def signup(user: User):
    try:
    
        existing_user = users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pw = hash_password(user.password)

        users_collection.insert_one({
            "email": user.email,
            "password": hashed_pw,
            "created_at": datetime.utcnow()
        })

        return {"message": "User registered successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")


@auth_router.post("/login")
def login(user: User):
    try:
        
        db_user = users_collection.find_one({"email": user.email})
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
           
        if not verify_password(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
 
        token = create_access_token({"sub": user.email})

        return {
            "access_token": token,
            "token_type": "bearer",
            "message": "Login successful"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
