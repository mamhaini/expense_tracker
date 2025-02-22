from utils import validate_user_by_token
from fastapi import HTTPException
from functools import wraps


def validate_user_decorator(func):
    """Decorator to validate token and fetch user email."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        token = kwargs.get('token')
        if not token:
            raise HTTPException(status_code=401, detail="Token is missing")
        try:
            user_email = await validate_user_by_token(token)
            kwargs['user_email'] = user_email
        except HTTPException:
            raise HTTPException(status_code=401, detail="Invalid token or user not found")
        return await func(*args, **kwargs)

    return wrapper
