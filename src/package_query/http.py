from typing import Any

from curl_cffi import AsyncSession
from orjson import loads


async def fetch_json(url: str, headers: dict[str, str]) -> Any:  # noqa: ANN401
    async with AsyncSession() as session:
        response = await session.get(url, headers=headers)

    if response.status_code == 404:
        raise ValueError("Not found")

    response.raise_for_status()

    return loads(response.content)
