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
        self.session = None

    async def _init_session(self):
        # Initialize the session when the event loop is running
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def _close_session(self):
        """Close the aiohttp session when no longer needed."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _request(self, method: str, endpoint: str, data=None, params=None, custom_headers=None):
        """
        Generic function to handle HTTP requests.
        """
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}/{endpoint}"

        # Merge default headers with any custom ones passed in
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

    async def sign_in(self, email, password):
        data = {"email": email, "password": password}
        return await self._request("POST", "auth/v1/token?grant_type=password", data=data)

    async def sign_up(self, email, password):
        data = {"email": email, "password": password}
        return await self._request("POST", "auth/v1/signup", data=data)

    async def delete_user(self, user_id: str, token: str):
        headers = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {token}"}
        # ToDo get correct endpoint
        return await self._request("DELETE", f"auth/v1/user/{user_id}", custom_headers=headers)

    async def select(self, table: str, token: str, params=None):
        headers = {"Authorization": f"Bearer {token}"}
        if params:
            params = {key: f"eq.{value}" for key, value in params.items()}
        return await self._request("GET", f"rest/v1/{table}", params=params, custom_headers=headers)

    async def insert(self, table: str, data: dict, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        return await self._request("POST", f"rest/v1/{table}", data=data, custom_headers=headers)

    async def update(self, table: str, filters: dict, data: dict, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        params = {key: f"eq.{value}" for key, value in filters.items()}
        return await self._request("PATCH", f"rest/v1/{table}", data=data, params=params,
                                   custom_headers=headers)

    async def delete(self, table: str, filters: dict, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        params = {key: f"eq.{value}" for key, value in filters.items()}
        return await self._request("DELETE", f"rest/v1/{table}", params=params, custom_headers=headers)
