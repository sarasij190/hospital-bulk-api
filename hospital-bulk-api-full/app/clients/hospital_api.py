""" 
Wrapper client for the external Hospital Directory API.
Uses httpx AsyncClient for async HTTP calls.
"""
from typing import Dict, Any, List
import httpx
import asyncio

class HospitalAPIClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self._timeout = timeout
        self._client = httpx.AsyncClient(timeout=self._timeout)

    async def create_hospital(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/hospitals/"
        resp = await self._client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

    async def activate_batch(self, batch_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/hospitals/batch/{batch_id}/activate"
        resp = await self._client.patch(url)
        resp.raise_for_status()
        return resp.json()

    async def get_batch(self, batch_id: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/hospitals/batch/{batch_id}"
        resp = await self._client.get(url)
        resp.raise_for_status()
        return resp.json()

    async def delete_batch(self, batch_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/hospitals/batch/{batch_id}"
        resp = await self._client.delete(url)
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self._client.aclose()
