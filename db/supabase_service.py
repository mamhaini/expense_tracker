from db import AsyncSupabaseClient
from dotenv import load_dotenv
from typing import Optional

import os

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client = AsyncSupabaseClient(SUPABASE_URL, SUPABASE_KEY)


class SupabaseService:
    def __init__(self):
        self.client = supabase_client

    # User-related methods
    async def register_user(self, email: str, password: str):
        # Check if the user already exists by email
        existing_user = self.get_user_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists.")

        # Register the user in Supabase Auth
        auth_response = await self.client.sign_up(email, password)

        # Add the user to the `users` table
        user_data = {"id": auth_response["id"], "email": email}
        await self.client.insert("users", user_data)
        return user_data

    async def login_user(self, email: str, password: str):
        return await self.client.sign_in(email, password)

    async def get_user_by_email(self, email: str):
        return await self.client.select("users", {"email": email})

    # Expense-related methods
    async def create_expense(self, user_id: str, amount: float, category: str, description: Optional[str] = None):
        expense_data = {"user_id": user_id, "amount": amount, "category": category, "description": description}
        return await self.client.insert("expenses", expense_data)

    async def get_expenses_by_user(self, user_id: str):
        return await self.client.select("expenses", {"user_id": user_id})

    async def update_expense(self, expense_id: int, data: dict):
        return await self.client.update("expenses", {"id": expense_id}, data)

    async def delete_expense(self, expense_id: int):
        return await self.client.delete("expenses", {"id": expense_id})

    # Category-related methods
    async def create_category(self, name: str):
        return await self.client.insert("categories", {"name": name})

    async def get_category_by_name(self, name: str):
        return await self.client.select("categories", {"name": name})

    async def get_all_categories(self):
        return await self.client.select("categories")


supabase = SupabaseService()
