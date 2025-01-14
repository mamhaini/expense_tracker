from utils import check_expense_authorization, check_category_exists
from models import ExpenseUpdate, ExpenseCreate
from typing import List
from db import supabase


class ExpenseService:
    @staticmethod
    async def create_expense(user: tuple, expense: ExpenseCreate) -> dict:
        """Create a new expense for the current user. Category should exist in predefined or user-created categories."""
        category_exists, _ = await check_category_exists(user, expense.category)
        return await supabase.create_expense(user, expense.amount, expense.category, expense.description)

    @staticmethod
    async def get_expenses_by_user(user: tuple) -> List[dict]:
        """Get all expenses for a specific user."""
        return await supabase.get_expenses_by_user(user)

    @staticmethod
    async def update_expense(expense_id: str, expense: ExpenseUpdate, user: tuple) -> dict:
        """Update an expense's details."""
        await check_expense_authorization(expense_id, user)
        if expense.category:
            category_exists, _ = await check_category_exists(user, expense.category)
        data = {key: value for key, value in expense.model_dump().items() if value is not None}
        return await supabase.update_expense(expense_id, data, user)

    @staticmethod
    async def delete_expense(expense_id: str, user: tuple) -> None:
        """Delete an expense by its ID."""
        await check_expense_authorization(expense_id, user)
        return await supabase.delete_expense(expense_id, user)
