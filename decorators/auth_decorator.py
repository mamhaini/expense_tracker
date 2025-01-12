from services.auth_service import AuthService
from fastapi import HTTPException
from functools import wraps

# Initialize AuthService
auth_service = AuthService()


def validate_user_decorator(func):
    """Decorator to validate token and fetch user email."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        token = kwargs.get('token')
        if not token:
            raise HTTPException(status_code=401, detail="Token is missing")
        try:
            user_email = auth_service.validate_user(token)
            kwargs['user_email'] = user_email
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token or user not found")
        return await func(*args, **kwargs)

    return wrapper
