from utils.constants import PREDEFINED_CATEGORIES
from typing import Optional, Tuple
from db import supabase


async def check_category_exists(user_id: str, category_name: str) -> Tuple[Optional[str], Optional[dict]]:
    """Check if a category exists in predefined or user-created categories."""

    # Check if the category is a predefined category
    predefined_category = next((cat for cat in PREDEFINED_CATEGORIES if cat["name"].lower() == category_name.lower()),
                               None)
    if predefined_category:
        return "predefined", predefined_category

    # Check if the category exists in the user's custom categories
    user_category = await supabase.get_user_category_by_name(user_id, category_name)
    if user_category:
        return "user", user_category

    return None, None
