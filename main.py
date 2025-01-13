from models import UserCredentials, ExpenseCreate, ExpenseUpdate, CategoryCreate
from utils import check_category_exists, PREDEFINED_CATEGORIES
from fastapi import FastAPI, HTTPException, Depends
from services.user_service import UserService
from contextlib import asynccontextmanager
from typing import List, AsyncIterator
from db import supabase

import uvicorn

# Initialize FastAPI app and services
user_service = UserService()


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
        return await supabase.register_user(user.email, user.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login", response_model=dict)
async def login(user: UserCredentials):
    """Log in an existing user."""
    try:
        return await supabase.login_user(user.email, user.password)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/users/{user_email}", response_model=dict)
async def get_user_by_email(user_email: str, user: dict = Depends(user_service.get_current_user)):
    """Get the profile of the current user if the email matches."""
    if user["email"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")
    return user


@app.delete("/users/{user_email}", status_code=204)
async def delete_user(user_email: str, user: dict = Depends(user_service.get_current_user)):
    """Delete the current user if the email matches."""
    if user["email"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to delete this profile")
    await supabase.delete_user(user["id"])


# Expense-related endpoints
@app.post("/expenses", status_code=201)
async def create_expense(expense: ExpenseCreate, user: dict = Depends(user_service.get_current_user)):
    """Create a new expense for the current user. The category should exist in predefined or user-created categories."""

    # Check if the category exists
    category_type, category = await check_category_exists(user["id"], expense.category)
    if not category:
        raise HTTPException(status_code=400, detail="Category does not exist.")

    return await supabase.create_expense(user["id"], **expense.model_dump())


@app.get("/expenses/{user_email}", response_model=List[dict])
async def get_expenses(user_email: str, user: dict = Depends(user_service.get_current_user)):
    """Retrieve all expenses for the specified user."""
    if user["email"] != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")
    return await supabase.get_expenses_by_user(user["id"])


@app.put("/expenses/{expense_id}", status_code=200)
async def update_expense(expense_id: str, expense: ExpenseUpdate, user: dict = Depends(user_service.get_current_user)):
    """Update an existing expense. The category should exist in predefined or user-created categories."""

    # Check if the category exists
    category_type, category = await check_category_exists(user["id"], expense.category)
    if not category:
        raise HTTPException(status_code=400, detail="Category does not exist.")

    return await supabase.update_expense(expense_id, expense.model_dump(exclude_unset=True))


@app.delete("/expenses/{expense_id}", status_code=204)
async def delete_expense(expense_id: str, user: dict = Depends(user_service.get_current_user)):
    """Delete an expense by its ID. The expense should belong to the current user."""

    # Check if the expense exists
    expense = await supabase.get_expense_by_id(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    # Check if the user is authorized to delete the expense
    if expense["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this expense")

    return await supabase.delete_expense(expense_id)


# Category-related endpoints
@app.post("/categories", status_code=201)
async def create_category(category: CategoryCreate, user: dict = Depends(user_service.get_current_user)):
    """Create a new category for the current user. The category name should not exist in predefined or user-created categories"""

    # Check if the category name already exists
    category_type, existing_category = await check_category_exists(user["id"], category.name)
    if category_type == "predefined":
        raise HTTPException(status_code=400, detail="Category name already exists in predefined categories.")
    if existing_category:
        raise HTTPException(status_code=400, detail="Category name already exists in your custom categories.")

    return await supabase.create_user_category(user["id"], category.name)


@app.get("/categories", response_model=List[dict])
async def get_all_categories(user: dict = Depends(user_service.get_current_user)):
    """Get all categories, including predefined and user-created ones."""
    user_created_categories = await supabase.get_user_categories(user["id"])
    return PREDEFINED_CATEGORIES + user_created_categories


@app.get("/categories/{category_name}", response_model=dict)
async def get_category_by_name(category_name: str, user: dict = Depends(user_service.get_current_user)):
    """Get a category by name from both predefined and user-created categories."""

    # Check if the category exists
    category_type, category = await check_category_exists(user["id"], category_name)
    if category:
        return category

    raise HTTPException(status_code=404, detail="Category not found")


@app.delete("/categories/{category_name}", status_code=204)
async def delete_category(category_name: str, user: dict = Depends(user_service.get_current_user)):
    """Delete a category if it's not linked to any expenses. The category should exist in user-created categories."""

    # Check if the category exists
    category_type, category = await check_category_exists(user["id"], category_name)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Ensure the category is not predefined before deletion
    if category_type == "predefined":
        raise HTTPException(status_code=400, detail="Cannot delete predefined category.")

    # Check if there are any expenses linked to the category
    linked_expenses = await supabase.get_expenses_by_user_and_category(user["id"], category_name)
    if linked_expenses:
        raise HTTPException(status_code=400, detail="Category is linked to one or more expenses. "
                                                    "Please update the expenses before deleting the category.")

    await supabase.delete_user_category(category["id"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
