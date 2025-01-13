from fastapi import HTTPException

import jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")


def validate_user(token: str):
    """Validate the JWT token and return the user's email."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_aud": False})
        email = payload.get("email")
        if email is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
