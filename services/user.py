from fastapi.security import OAuth2PasswordBearer
from decorators import validate_user_decorator
from fastapi import HTTPException, Depends
from aiohttp import ClientResponseError
from models import UserCredentials
from db import supabase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User:
    @staticmethod
    @validate_user_decorator
    async def validate(token: str = Depends(oauth2_scheme), user_email: str = None) -> tuple[dict, str]:
        """Validate the user's token and retrieve their profile."""
        try:
            user = await supabase.get_user_by_email(user_email, token)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user, token
        except ClientResponseError:
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    async def register(user: UserCredentials):
        """Register a new user."""
        try:
            return await supabase.register_user(user.email, user.password)
        except ClientResponseError as e:
            raise HTTPException(status_code=400, detail=e.message)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=e.args[0])

    @staticmethod
    async def forgot_password(email: str):
        """Send a password reset link to the user's email."""
        try:
            return await supabase.send_password_reset_email(email)
        except ClientResponseError as e:
            raise HTTPException(status_code=400, detail=e.message)

    @staticmethod
    async def login(user: UserCredentials):
        """Log in an existing user."""
        try:
            return await supabase.login_user(user.email, user.password)
        except ClientResponseError as e:
            raise HTTPException(status_code=401, detail=e.message)

    @staticmethod
    async def refresh(refresh_token: str):
        """Refresh the access token using the refresh token."""
        try:
            return await supabase.refresh_token(refresh_token)
        except ClientResponseError as e:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    @staticmethod
    async def delete(user_email: str, user: dict):
        """Delete the current user if the email matches."""
        if user["email"] != user_email:
            raise HTTPException(status_code=403, detail="Not authorized to delete this profile")
        await supabase.delete_user(user["id"])
