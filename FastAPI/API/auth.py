import jwt
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

# Secret key to sign and verify JWT tokens
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Function to create JWT tokens
def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to decode JWT tokens
def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Handle token expiration here
        return JSONResponse(content = {"conn_status":"f","message":"token expired"})
    except jwt.InvalidTokenError:
        # Handle other token validation errors here
        return JSONResponse(content = {"conn_status":"f","message":"invalid token"})


