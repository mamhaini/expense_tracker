from db import AsyncSupabaseClient
from dotenv import load_dotenv
from typing import Optional

import os

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")


class Supabase:
    def __init__(self):
        self.client = AsyncSupabaseClient(SUPABASE_URL, SUPABASE_KEY)  # Initialize the Supabase client

    # User-related methods
    async def register_user(self, email: str, password: str) -> dict:
        """Register a new user if the user exists."""
        existing_user = await self.get_user_by_email(email, SUPABASE_KEY)
        if existing_user:
            raise ValueError(f"User with email {email} already exists.")

        return await self.client.sign_up(email, password)

    async def send_password_reset_email(self, email: str) -> dict:
        """Send a password reset email to the user."""
        return await self.client.send_password_reset_email(email)

    async def login_user(self, email: str, password: str) -> dict:
        """Log in a user using their email and password. Add them to the `users` table if they don't exist."""
        existing_user = await self.get_user_by_email(email, SUPABASE_KEY)
        login_response = await self.client.sign_in(email, password)

        user_data = {"id": login_response["user"]["id"], "email": email}
        if not existing_user:
            await self.client.insert("users", user_data, SUPABASE_KEY)

        return login_response

    async def refresh_token(self, refresh_token: str) -> dict:
        """Refresh the access token using the refresh token."""
        return await self.client.refresh_token(refresh_token)

    async def delete_user(self, user_id: str):
        """Delete a user by their ID."""
        return await self.client.delete_user(user_id)

    async def get_user_by_email(self, email: str, token: str) -> Optional[dict]:
        """Retrieve a user by their email."""
        user = await self.client.select("users", token, {"email": email})
        return user[0] if user else None

    # Expense-related methods
    async def create_expense(self, user: tuple, amount: float, category: str, description: Optional[str] = None):
        """Create an expense for a user."""
        expense_data = {"user_id": user[0]["id"], "amount": amount, "category": category.lower(),
                        "description": description}
        expense = await self.client.insert("expenses", expense_data, user[1])
        return expense[0] if expense else {}

    async def get_expense_by_id(self, expense_id: str, user: tuple) -> Optional[dict]:
        """Get an expense by its ID."""
        expenses = await self.client.select("expenses", user[1], {"id": expense_id})
        return expenses[0] if expenses else None

    async def get_expenses_by_user(self, user: tuple):
        """Get all expenses for a specific user."""
        return await self.client.select("expenses", user[1], {"user_id": user[0]["id"]})

    async def get_expenses_by_user_and_category(self, user: tuple, category: str):
        """Get expenses for a specific user and category."""
        params = {"user_id": user[0]["id"], "category": category.lower()}
        return await self.client.select("expenses", user[1], params)

    async def update_expense(self, expense_id: str, data: dict, user: tuple):
        """Update an expense's details."""
        expense = await self.client.update("expenses", {"id": expense_id}, data, user[1])
        return expense[0] if expense else {}

    async def delete_expense(self, expense_id: str, user: tuple):
        """Delete an expense by its ID."""
        return await self.client.delete("expenses", {"id": expense_id}, user[1])

    # Category-related methods
    async def create_user_category(self, user: tuple, category_name: str):
        """Create a custom category for a user."""
        data = {"user_id": user[0]["id"], "name": category_name.lower()}
        category = await self.client.insert("categories", data, user[1])
        return category[0] if category else {}

    async def get_user_categories(self, user: tuple):
        """Get all categories for a specific user."""
        return await self.client.select("categories", user[1], {"user_id": user[0]["id"]})

    async def get_user_category_by_name(self, user: tuple, category_name: str) -> Optional[dict]:
        """Get a specific category by name for a user."""
        params = {"user_id": user[0]["id"], "name": category_name.lower()}
        cats = await self.client.select("categories", user[1], params)
        return cats[0] if cats else None

    async def delete_user_category(self, category_id: str, user: tuple):
        """Delete a category by its ID."""
        return await self.client.delete("categories", {"id": category_id}, user[1])


supabase = Supabase()
