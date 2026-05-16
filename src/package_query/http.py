from typing import Any

from curl_cffi import AsyncSession
from orjson import loads

from package_query.exceptions import PackageNotFoundError, RegistryError


async def fetch_json(url: str, headers: dict[str, str]) -> Any:  # noqa: ANN401
    async with AsyncSession() as session:
        response = await session.get(url, headers=headers)

    if response.status_code == 404:
        raise PackageNotFoundError("Not found")

    if not response.ok:
        raise RegistryError(f"Registry returned HTTP {response.status_code}")

    return loads(response.content)
