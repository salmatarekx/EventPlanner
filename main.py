from fastapi import FastAPI
from routes.auth_routes import auth_router
from database import connect_to_mongo
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EventPlanner API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db_client():
    connect_to_mongo()

@app.get("/")
def root():
    return {
        "message": "Welcome to EventPlanner API",
        "version": "1.0.0",
        "phase": "Phase 0 - User Management",
        "status": "active"
    }

@app.get("/test-db")
def test_db():
    from database import db
    try:
        if db is None:
            return {"error": "Database not connected"}
        db.list_collection_names()
        return {"message": "MongoDB connection successful!"}
    except Exception as e:
        return {"error": str(e)}

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
