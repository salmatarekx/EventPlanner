import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY missing from .env file")
SECRET_KEY = SECRET_KEY.strip()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
