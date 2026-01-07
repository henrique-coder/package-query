from typing import Any

import orjson
from curl_cffi.requests import AsyncSession


async def fetch_json(url: str, headers: dict[str, str]) -> dict[str, Any]:
    async with AsyncSession() as session:
        response = await session.get(url, headers=headers)
    if response.status_code == 404:
        raise ValueError("Not found")
    response.raise_for_status()
    return orjson.loads(response.content)
