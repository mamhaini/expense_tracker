from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import SupabaseService

import uvicorn

# Initialize FastAPI app and SupabaseService
app = FastAPI()
supabase_service = SupabaseService()


class UserAuthenticationRequest(BaseModel):
    email: str
    password: str


@app.post("/register")
async def register(user: UserAuthenticationRequest):
    try:
        return await supabase_service.register_user(user.email, user.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login")
async def login(user: UserAuthenticationRequest):
    try:
        return await supabase_service.login_user(user.email, user.password)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/user")
async def get_user(email: str):
    try:
        return await supabase_service.get_user_by_email(email)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
