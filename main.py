from fastapi import FastAPI
from routes.auth_routes import auth_router
from routes.event_routes import event_router
from database import connect_to_mongo
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EventPlanner API", version="1.0.0")

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

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(event_router, prefix="/events", tags=["Events"])
