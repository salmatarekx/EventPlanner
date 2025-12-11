from fastapi import APIRouter
import database  # note: import the module, not the variable

test_router = APIRouter()

@test_router.get("/test-db", summary="Test db")
def test_db():
    database.connect_to_mongo()

    result = database.users_collection.insert_one({
        "name": "DB Test User",
        "status": "connected"
    })

    return {"inserted_id": str(result.inserted_id)}
