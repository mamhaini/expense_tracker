from fastapi.security import OAuth2PasswordBearer
from decorators import validate_user_decorator
from fastapi import HTTPException, Depends
from models import UserCredentials
from db import supabase

# Initialize OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@validate_user_decorator
async def validate_user(token: str = Depends(oauth2_scheme), user_email: str = None) -> tuple[dict, str]:
    """Validate the user's token and retrieve their profile."""
    try:
        user = await supabase.get_user_by_email(user_email, token)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user, token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


async def register_user(user: UserCredentials):
    """Register a new user."""
    return await supabase.register_user(user.email, user.password)


async def login_user(user: UserCredentials):
    """Log in an existing user."""
    return await supabase.login_user(user.email, user.password)


async def delete_user(user_email: str, user: dict, token: str):
    """Delete the current user if the email matches."""
    if user["email"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to delete this profile")
    await supabase.delete_user(user["id"], token)
