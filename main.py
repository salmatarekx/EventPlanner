from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth_routes import auth_router
from routes.event_routes import event_router
from routes.response_routes import response_router
from routes.search_routes import search_router
from database import connect_to_mongo
from routes.test_routes import test_router


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
app.include_router(response_router, prefix="/events", tags=["Response Management"])
app.include_router(search_router, prefix="/events", tags=["Search & Filtering"])
app.include_router(test_router, tags=["Test"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

