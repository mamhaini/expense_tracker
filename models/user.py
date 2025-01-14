from pydantic import BaseModel


class UserCredentials(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str
