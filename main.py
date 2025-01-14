from models import UserCredentials, ExpenseCreate, ExpenseUpdate, CategoryCreate
from services import CategoryService, ExpenseService, UserService
from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
from typing import List, AsyncIterator
from db import supabase

import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Function to manage the lifespan of the FastAPI application. Closes DB session when the app is shut down."""
    await supabase.client._init_session()
    yield
    await supabase.client._close_session()


app = FastAPI(lifespan=lifespan)


# User endpoints
@app.post("/register", response_model=dict)
async def register(user: UserCredentials):
    """Register a new user."""
    try:
        return await UserService.register_user(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login", response_model=dict)
async def login(user: UserCredentials):
    """Log in an existing user."""
    try:
        return await UserService.login_user(user)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/users/{user_email}", response_model=dict)
async def get_user_by_email(user_email: str, user: tuple = Depends(UserService.validate_user)):
    """Get the profile of the current user if the email matches."""

    # Check if the user is authorized to view the profile
    if user[0]["email"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")

    return user[0]


@app.delete("/users/{user_email}", status_code=204)
async def delete_user(user_email: str, user: tuple = Depends(UserService.validate_user)):
    """Delete the current user if the email matches."""
    await UserService.delete_user(user_email, user[0], user[1])


# Expense-related endpoints
@app.post("/expenses", status_code=201, response_model=dict)
async def create_expense(expense: ExpenseCreate, user: tuple = Depends(UserService.validate_user)) -> dict:
    """Create a new expense for the current user. The category should exist in predefined or user-created categories."""
    return await ExpenseService.create_expense(user, expense)


@app.get("/expenses/{user_email}", response_model=List[dict])
async def get_expenses(user_email: str, user: tuple = Depends(UserService.validate_user)):
    """Retrieve all expenses for the specified user."""

    # Check if the user is authorized to view the expenses
    if user[0]["email"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")

    return await ExpenseService.get_expenses_by_user(user)


@app.put("/expenses/{expense_id}", status_code=200, response_model=dict)
async def update_expense(expense_id: str, expense: ExpenseUpdate, user: tuple = Depends(UserService.validate_user)):
    """Update an existing expense. The category should exist in predefined or user-created categories."""
    return await ExpenseService.update_expense(expense_id, expense, user)


@app.delete("/expenses/{expense_id}", status_code=204)
async def delete_expense(expense_id: str, user: tuple = Depends(UserService.validate_user)):
    """Delete an expense by its ID. The expense should belong to the current user."""
    return await ExpenseService.delete_expense(expense_id, user)


# Category-related endpoints
@app.post("/categories", status_code=201, response_model=dict)
async def create_category(category: CategoryCreate, user: tuple = Depends(UserService.validate_user)):
    """Create a new category for the current user. The category name should not exist in predefined or user-created categories"""
    return await CategoryService.create_category(user, category.name)


@app.get("/categories", response_model=List[dict])
async def get_all_categories(user: tuple = Depends(UserService.validate_user)):
    """Get all categories, including predefined and user-created ones."""
    return await CategoryService.get_all_categories(user)


@app.get("/categories/{category_name}", response_model=dict)
async def get_category_by_name(category_name: str, user: tuple = Depends(UserService.validate_user)):
    """Get a category by name from both predefined and user-created categories."""
    return await CategoryService.get_category_by_name(user, category_name)


@app.delete("/categories/{category_name}", status_code=204)
async def delete_category(category_name: str, user: tuple = Depends(UserService.validate_user)):
    """Delete a category if it's not linked to any expenses. The category should exist in user-created categories."""
    return await CategoryService.delete_category(user, category_name)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
