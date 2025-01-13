from db import AsyncSupabaseClient
from dotenv import load_dotenv
from typing import Optional

import os

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")


class SupabaseService:
    def __init__(self):
        self.client = AsyncSupabaseClient(SUPABASE_URL, SUPABASE_KEY)  # Initialize the Supabase client

    # User-related methods
    async def register_user(self, email: str, password: str) -> dict:
        """Register a new user, creating them in Supabase Auth and the `users` table."""
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists.")

        auth_response = await self.client.sign_up(email, password)

        user_data = {"id": auth_response["id"], "email": email}
        await self.client.insert("users", user_data)
        return user_data

    async def login_user(self, email: str, password: str) -> dict:
        """Log in a user using their email and password."""
        return await self.client.sign_in(email, password)

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Retrieve a user by their email."""
        user = await self.client.select("users", {"email": email})
        return user[0] if user else None

    # Expense-related methods
    async def create_expense(self, user_id: str, amount: float, category: str, description: Optional[str] = None):
        """Create an expense for a user."""
        expense_data = {"user_id": user_id, "amount": amount, "category": category.lower(), "description": description}
        return await self.client.insert("expenses", expense_data)

    async def get_expense_by_id(self, expense_id: str):
        """Get an expense by its ID."""
        return await self.client.select("expenses", {"id": expense_id})

    async def get_expenses_by_user(self, user_id: str):
        """Get all expenses for a specific user."""
        return await self.client.select("expenses", {"user_id": user_id})

    async def get_expenses_by_user_and_category(self, user_id: str, category: str):
        """Get expenses for a specific user and category."""
        return await self.client.select("expenses", {"user_id": user_id, "category": category.lower()})

    async def update_expense(self, expense_id: str, data: dict):
        """Update an expense's details."""
        return await self.client.update("expenses", {"id": expense_id}, data)

    async def delete_expense(self, expense_id: str):
        """Delete an expense by its ID."""
        return await self.client.delete("expenses", {"id": expense_id})

    # Category-related methods
    async def create_user_category(self, user_id: str, category_name: str):
        """Create a custom category for a user."""
        return await self.client.insert("categories", {"user_id": user_id, "name": category_name.lower()})

    async def get_user_categories(self, user_id: str):
        """Get all categories for a specific user."""
        return await self.client.select("categories", {"user_id": user_id})

    async def get_user_category_by_name(self, user_id: str, category_name: str) -> Optional[dict]:
        """Get a specific category by name for a user."""
        cats = await self.client.select("categories", {"user_id": user_id, "name": category_name.lower()})
        return cats[0] if cats else None

    async def delete_user_category(self, category_id: str):
        """Delete a category by its ID."""
        return await self.client.delete("categories", {"id": category_id})


supabase = SupabaseService()
