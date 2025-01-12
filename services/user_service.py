from fastapi.security import OAuth2PasswordBearer
from decorators import validate_user_decorator
from fastapi import HTTPException, Depends
from db import supabase

# Initialize OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserService:
    @validate_user_decorator
    async def get_current_user(self, token: str = Depends(oauth2_scheme), user_email: str = None):
        """Fetch the user based on the email after validating the token."""
        user = await supabase.get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
