"""{{API_NAME}} async HTTP client with auth, pagination, and rate limiting."""

import asyncio
import os
from typing import Any, Optional

import httpx

API_VERSION = "{{API_VERSION}}"
BASE_URL = "{{BASE_URL}}"


class ApiError(Exception):
    """Error from the API."""

    def __init__(self, message: str, status_code: int = 0):
        self.status_code = status_code
        super().__init__(message)


class RateLimitError(ApiError):
    """Rate limit hit — caller should retry with backoff."""
    pass


class ApiClient:
    """Async HTTP client for {{API_NAME}}."""

    def __init__(self):
        self._token = os.environ.get("{{ENV_VAR_TOKEN}}", "")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=BASE_URL,
                timeout=httpx.Timeout(30.0, read=60.0),
                limits=httpx.Limits(max_connections=20),
            )
        return self._client

    def _auth_params(self) -> dict[str, str]:
        # Adapt auth strategy: bearer token, API key, etc.
        return {"access_token": self._token}

    def _auth_headers(self) -> dict[str, str]:
        # Alternative: use Authorization header
        # return {"Authorization": f"Bearer {self._token}"}
        return {}

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make an authenticated request."""
        client = await self._get_client()
        all_params = {**self._auth_params(), **(params or {})}
        headers = self._auth_headers()

        for attempt in range(3):
            response = await client.request(
                method,
                endpoint if endpoint.startswith("http") else f"/{endpoint.lstrip('/')}",
                params=all_params,
                data=data,
                headers=headers,
            )

            if response.status_code == 200:
                return response.json()

            if response.status_code == 429:
                if attempt < 2:
                    await asyncio.sleep(2 ** (attempt + 1))
                    continue
                raise RateLimitError(response.text, status_code=429)

            raise ApiError(response.text, status_code=response.status_code)

        raise ApiError("Max retries exceeded")

    async def get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return await self.request("GET", endpoint, params=params)

    async def post(self, endpoint: str, params: Optional[dict[str, Any]] = None, data: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return await self.request("POST", endpoint, params=params, data=data)

    async def delete(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return await self.request("DELETE", endpoint, params=params)

    async def get_all_pages(self, endpoint: str, params: Optional[dict[str, Any]] = None, max_pages: int = 50) -> list[dict[str, Any]]:
        """Fetch all pages of a paginated endpoint."""
        all_data: list[dict[str, Any]] = []
        result = await self.get(endpoint, params=params)
        all_data.extend(result.get("data", []))

        pages = 1
        while pages < max_pages:
            next_url = result.get("paging", {}).get("next")
            if not next_url:
                break
            result = await self.get(next_url)
            all_data.extend(result.get("data", []))
            pages += 1

        return all_data

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
