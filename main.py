from fastapi import FastAPI, HTTPException, Depends
from services.user_service import UserService
from models import UserCredentials
from db import supabase

import uvicorn

# Initialize FastAPI app and services
app = FastAPI()
user_service = UserService()


@app.post("/register")
async def register(user: UserCredentials):
    try:
        return await supabase.register_user(user.email, user.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login")
async def login(user: UserCredentials):
    try:
        return await supabase.login_user(user.email, user.password)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/users/{email}")
async def get_user_by_email(email: str, current_user: dict = Depends(user_service.get_current_user)):
    if current_user["email"] != email:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")
    return current_user


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
