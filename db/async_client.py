import aiohttp


class AsyncSupabaseClient:
    def __init__(self, url: str, key: str):
        self.base_url = url
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
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

    async def _request(self, method: str, endpoint: str, data=None, params=None):
        """
        Generic function to handle HTTP requests.
        """
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}/{endpoint}"
        async with self.session.request(
                method, url, headers=self.headers, json=data, params=params
        ) as response:
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
            return await response.text()

    async def sign_in(self, email, password):
        data = {"email": email, "password": password}
        return await self._request("POST", "auth/v1/token?grant_type=password", data=data)

    async def sign_up(self, email, password):
        data = {"email": email, "password": password}
        return await self._request("POST", "auth/v1/signup", data=data)

    async def select(self, table: str, params=None):
        if params:
            params = {key: f"eq.{value}" for key, value in params.items()}
        return await self._request("GET", f"rest/v1/{table}", params=params)

    async def insert(self, table: str, data: dict):
        return await self._request("POST", f"rest/v1/{table}", data=data)

    async def update(self, table: str, filters: dict, data: dict):
        params = {key: f"eq.{value}" for key, value in filters.items()}
        return await self._request("PATCH", f"rest/v1/{table}", data=data, params=params)

    async def delete(self, table: str, filters: dict):
        params = {key: f"eq.{value}" for key, value in filters.items()}
        return await self._request("DELETE", f"rest/v1/{table}", params=params)
