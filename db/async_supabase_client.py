from typing import Optional

import aiohttp
import os

SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


class AsyncSupabaseClient:
    def __init__(self, url: str, key: str):
        self.base_url = url
        self.headers = {
            "apikey": key,
            "Content-Type": "application/json",
            "prefer": "return=representation",
        }
        self.session: Optional[aiohttp.ClientSession] = None

    async def _init_session(self) -> None:
        """Initialize the aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def _close_session(self) -> None:
        """Close the aiohttp session when no longer needed."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _request(self, method: str, endpoint: str, data: Optional[dict] = None, params: Optional[dict] = None,
                       custom_headers: Optional[dict] = None) -> Optional[dict]:
        """Generic function to handle HTTP requests."""
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}/{endpoint}"
        headers = {**self.headers, **(custom_headers or {})}

        async with self.session.request(method, url, headers=headers, json=data, params=params) as response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                error_text = await response.text()
                raise aiohttp.ClientResponseError(
                    request_info=e.request_info,
                    history=e.history,
                    status=e.status,
                    message=f"{e.message}: {error_text}",
                    headers=e.headers,
                )
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return await response.json()
            text = await response.text()
            return text if text else None

    async def sign_up(self, email: str, password: str) -> dict:
        """Sign up a new user."""
        data = {"email": email, "password": password}
        return await self._request("POST", "auth/v1/signup", data=data)

    async def sign_in(self, email: str, password: str) -> dict:
        """Sign in an existing user."""
        data = {"email": email, "password": password}
        return await self._request("POST", "auth/v1/token?grant_type=password", data=data)

    async def refresh_token(self, refresh_token: str) -> dict:
        """Refresh the access token using the refresh token."""
        data = {"refresh_token": refresh_token}
        return await self._request("POST", "auth/v1/token?grant_type=refresh_token", data=data)

    async def delete_user(self, user_id: str) -> None:
        """Delete a user from Supabase Authentication and the database."""
        headers = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}"}
        await self._request("DELETE", f"auth/v1/admin/users/{user_id}", custom_headers=headers)
        await self._request("DELETE", f"rest/v1/users", params={"id": f"eq.{user_id}"}, custom_headers=headers)

    async def select(self, table: str, token: str, params: Optional[dict] = None) -> Optional[dict]:
        """Select data from a table."""
        headers = {"Authorization": f"Bearer {token}"}
        if params:
            params = {key: f"eq.{value}" for key, value in params.items()}
        return await self._request("GET", f"rest/v1/{table}", params=params, custom_headers=headers)

    async def insert(self, table: str, data: dict, token: str) -> Optional[dict]:
        """Insert data into a table."""
        headers = {"Authorization": f"Bearer {token}"}
        return await self._request("POST", f"rest/v1/{table}", data=data, custom_headers=headers)

    async def update(self, table: str, filters: dict, data: dict, token: str) -> Optional[dict]:
        """Update data in a table."""
        headers = {"Authorization": f"Bearer {token}"}
        params = {key: f"eq.{value}" for key, value in filters.items()}
        return await self._request("PATCH", f"rest/v1/{table}", data=data, params=params, custom_headers=headers)

    async def delete(self, table: str, filters: dict, token: str) -> Optional[dict]:
        """Delete data from a table."""
        headers = {"Authorization": f"Bearer {token}"}
        params = {key: f"eq.{value}" for key, value in filters.items()}
        return await self._request("DELETE", f"rest/v1/{table}", params=params, custom_headers=headers)
