from fastapi import FastAPI
from routes.auth_routes import auth_router
from database import connect_to_mongo

app = FastAPI(
    title="EventPlanner API",
    version="1.0.0"
)

# Run Mongo connection during startup
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
    from database import db  # ✅ re-import inside the function to get the updated db reference
    try:
        if db is None:
            return {"error": "Database not connected"}
        db.list_collection_names()
        return {"message": "MongoDB connection successful!"}
    except Exception as e:
        return {"error": str(e)}

# include routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
