from models import (UserCredentials, ExpenseCreate, ExpenseUpdate, CategoryCreate, RefreshRequest, UserResponse,
                    ExpenseResponse, CategoryResponse)
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from services import User, Expense, Category
from contextlib import asynccontextmanager
from typing import List, AsyncIterator
from pydantic import EmailStr
from db import supabase

import uvicorn
import os


# ToDo should probably add mass delete and update endpoints for expenses and categories
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Function to manage the lifespan of the FastAPI application. Closes DB session when the app is shut down."""
    await supabase.client._init_session()
    yield
    await supabase.client._close_session()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:5000", "http://localhost:5173",
                   "https://expense-tracker-s31f.onrender.com", "https://expense-tracker-ui-j78v.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# User endpoints
@app.post("/register", response_model=dict)
async def register(user: UserCredentials):
    """Register a new user."""
    return await User.register(user)


@app.post("/forgot-password", response_model=dict)
async def forgot_password(email: EmailStr):
    """Send a password reset link to the user's email."""
    return await User.forgot_password(email)


@app.post("/login", response_model=dict)
async def login(user: UserCredentials):
    """Log in an existing user."""
    return await User.login(user)


@app.post("/refresh", response_model=dict)
async def refresh(request: RefreshRequest):
    """Refresh the access token using the refresh token."""
    return await User.refresh(request.refresh_token)


@app.get("/users/{user_email}", response_model=UserResponse)
async def get_user_by_email(user_email: EmailStr, user: tuple = Depends(User.validate)):
    """Get the profile of the current user if the email matches. Validate already returns the user_data"""

    # Check if the user is authorized to view the profile
    if user[0]["email"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")

    return user[0]


@app.delete("/users/{user_email}", status_code=204)
async def delete_user(user_email: EmailStr, user: tuple = Depends(User.validate)):
    """Delete the current user if the email matches."""
    await User.delete(user_email, user[0])


# Expense-related endpoints
@app.post("/expenses", status_code=201, response_model=ExpenseResponse)
async def create_expense(expense: ExpenseCreate, user: tuple = Depends(User.validate)) -> dict:
    """Create a new expense for the current user. The category should exist in predefined or user-created categories."""
    return await Expense.create(user, expense)


@app.get("/expenses/{user_email}", response_model=List[ExpenseResponse])
async def get_expenses(user_email: EmailStr, user: tuple = Depends(User.validate)):
    """Retrieve all expenses for the specified user."""

    # Check if the user is authorized to view the expenses
    if user[0]["email"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")

    return await Expense.get_by_user(user)


@app.put("/expenses/{expense_id}", status_code=200, response_model=ExpenseResponse)
async def update_expense(expense_id: str, expense: ExpenseUpdate, user: tuple = Depends(User.validate)):
    """Update an existing expense. The category should exist in predefined or user-created categories."""
    return await Expense.update(expense_id, expense, user)


@app.delete("/expenses/{expense_id}", status_code=204)
async def delete_expense(expense_id: str, user: tuple = Depends(User.validate)):
    """Delete an expense by its ID. The expense should belong to the current user."""
    return await Expense.delete(expense_id, user)


# Category-related endpoints
@app.post("/categories", status_code=201, response_model=CategoryResponse)
async def create_category(category: CategoryCreate, user: tuple = Depends(User.validate)):
    """Create a new category for the current user. The category name should not exist in predefined or user-created categories"""
    return await Category.create(user, category.name)


@app.get("/categories", response_model=List[CategoryResponse])
async def get_all_categories(user: tuple = Depends(User.validate)):
    """Get all categories, including predefined and user-created ones."""
    return await Category.get_all(user)


@app.get("/categories/{category_name}", response_model=CategoryResponse)
async def get_category_by_name(category_name: str, user: tuple = Depends(User.validate)):
    """Get a category by name from both predefined and user-created categories."""
    return await Category.get_by_name(user, category_name)


@app.delete("/categories/{category_name}", status_code=204)
async def delete_category(category_name: str, user: tuple = Depends(User.validate)):
    """Delete a category if it's not linked to any expenses. The category should exist in user-created categories."""
    return await Category.delete(user, category_name)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
