import os
import logging
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY missing from .env file")

SECRET_KEY = SECRET_KEY.strip()
print("auth_utils loaded, SECRET_KEY =", SECRET_KEY, "| type:", type(SECRET_KEY))

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# logger = logging.getLogger("auth_utils")
# if not logger.handlers:
#     handler = logging.StreamHandler()
#     formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)
# logger.setLevel(logging.INFO)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    print("⚡ create_access_token CALLED")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    print("DEBUG SECRET_KEY =", SECRET_KEY, "| type:", type(SECRET_KEY))
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # logger.info(f"JWT generated for {data.get('sub')}: {token}")
    print("Token created successfully!")
    return token
