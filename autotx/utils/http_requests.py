from typing import Any
import aiohttp


async def get(url: str, params: dict[str, Any] = {}, headers: dict[str, Any] | None = None) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        return await session.get(url, params=params, headers=headers)
    
async def post(url: str, headers: dict[str, Any] | None = None, json: dict[str, Any] = {}, data: Any = None) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        return await session.post(url, headers=headers, json=json, data=data)
