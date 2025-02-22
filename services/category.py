from utils import check_category_exists, PREDEFINED_CATEGORIES
from fastapi import HTTPException
from typing import List
from db import supabase


class Category:
    @staticmethod
    async def create(user: tuple, category_name: str) -> dict:
        """Create a new category for the current user."""
        category_type, existing_category = await check_category_exists(user, category_name, raise_exception=False)
        if category_type == "predefined":
            raise HTTPException(status_code=400, detail="Category name already exists in predefined categories.")
        if existing_category:
            raise HTTPException(status_code=400, detail="Category name already exists in your custom categories.")
        return await supabase.create_user_category(user, category_name)

    @staticmethod
    async def get_all(user: tuple) -> List[dict]:
        """Get all categories, including predefined and user-created ones."""
        return PREDEFINED_CATEGORIES + await supabase.get_user_categories(user)

    @staticmethod
    async def get_by_name(user: tuple, category_name: str) -> dict:
        """Get a category by name from both predefined and user-created categories."""
        return (await check_category_exists(user, category_name))[1]

    @staticmethod
    async def delete(user: tuple, category_name: str) -> None:
        """Delete a category if it's not linked to any expenses."""
        category_type, category = await check_category_exists(user, category_name)
        if category_type == "predefined":
            raise HTTPException(status_code=400, detail="Cannot delete predefined category.")
        linked_expenses = await supabase.get_expenses_by_user_and_category(user, category_name)
        if linked_expenses:
            raise HTTPException(status_code=400, detail="Category is linked to one or more expenses. "
                                                        "Please update the expenses before deleting the category.")
        await supabase.delete_user_category(category["id"], user)
