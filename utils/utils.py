from utils.constants import PREDEFINED_CATEGORIES
from fastapi import HTTPException
from typing import Tuple, Optional
from db import supabase


async def check_category_exists(user: tuple, category_name: str,
                                raise_exception: bool = True) -> Tuple[Optional[str], Optional[dict]]:
    """Check if a category exists in predefined or user-created categories."""

    # Check if the category is a predefined category
    predefined_category = next((cat for cat in PREDEFINED_CATEGORIES if cat["name"].lower() == category_name.lower()),
                               None)
    if predefined_category:
        return "predefined", predefined_category

    # Check if the category exists in the user's custom categories
    user_category = await supabase.get_user_category_by_name(user, category_name)
    if user_category:
        return "user", user_category

    # Raise an exception if the category doesn't exist (Used for most cases)
    if raise_exception:
        raise HTTPException(status_code=404, detail="Category not found")
    return None, None


async def check_expense_authorization(expense_id: str, user: tuple) -> dict:
    """Check if the user is authorized to access the expense and if the expense exists."""
    existing_expense = await supabase.get_expense_by_id(expense_id, user)
    if not existing_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if existing_expense["user_id"] != user[0]["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this expense")
    return existing_expense
