from __future__ import annotations

from datetime import datetime
from typing import Final, Protocol

from curl_cffi.requests import AsyncSession
from orjson import loads

from package_query.constants import HTTP_HEADERS, PYPI_PACKAGE_PATTERN
from package_query.exceptions import InvalidPackageNameError, PackageNotFoundError
from package_query.models import PackageInfo


class PyPISourceProtocol(Protocol):
    NAME: str

    async def fetch(self, package: str, include_prerelease: bool = False) -> PackageInfo: ...


class PyPIPiwheelsSource:
    NAME: Final[str] = "piwheels"
    BASE_URL: Final[str] = "https://www.piwheels.org/project"

    async def fetch(self, package: str, include_prerelease: bool = False) -> PackageInfo:
        url: str = f"{self.BASE_URL}/{package}/json/"

        async with AsyncSession() as session:
            response = await session.get(url, headers=HTTP_HEADERS)

        if response.status_code == 404:
            raise PackageNotFoundError(f"Package '{package}' not found on piwheels")

        response.raise_for_status()
        data: dict = loads(response.content)
        releases: dict = data.get("releases", {})

        if not releases:
            raise PackageNotFoundError(f"Package '{package}' has no releases on piwheels")

        latest_version: str | None = None
        latest_released: datetime | None = None
        is_prerelease: bool = False

        for version, info in releases.items():
            if info.get("yanked", False):
                continue
            released_str: str | None = info.get("released")
            if not released_str:
                continue
            released: datetime = datetime.fromisoformat(released_str.replace(" ", "T"))
            version_is_prerelease: bool = info.get("prerelease", False)

            if (include_prerelease or not version_is_prerelease) and (
                latest_released is None or released > latest_released
            ):
                latest_version = version
                latest_released = released
                is_prerelease = version_is_prerelease

        if latest_version is None:
            raise PackageNotFoundError(f"Package '{package}' has no valid releases on piwheels")

        return PackageInfo(
            name=data.get("package", package),
            version=latest_version,
            registry=PyPIProvider.REGISTRY_NAME,
            is_prerelease=is_prerelease,
        )


class PyPIOfficialSource:
    NAME: Final[str] = "pypi"
    BASE_URL: Final[str] = "https://pypi.org/pypi"

    async def fetch(self, package: str, include_prerelease: bool = False) -> PackageInfo:
        url: str = f"{self.BASE_URL}/{package}/json"

        async with AsyncSession() as session:
            response = await session.get(url, headers=HTTP_HEADERS)

        if response.status_code == 404:
            raise PackageNotFoundError(f"Package '{package}' not found on PyPI")

        response.raise_for_status()
        data: dict = loads(response.content)

        info: dict = data.get("info", {})
        version: str = info.get("version", "")

        return PackageInfo(
            name=info.get("name", package),
            version=version,
            registry=PyPIProvider.REGISTRY_NAME,
            is_prerelease=False,
        )


class PyPIProvider:
    REGISTRY_NAME: Final[str] = "pypi"
    SOURCES: Final[list[type[PyPISourceProtocol]]] = [PyPIOfficialSource, PyPIPiwheelsSource]
    SOURCE_MAP: Final[dict[str, type[PyPISourceProtocol]]] = {
        "pypi": PyPIOfficialSource,
        "piwheels": PyPIPiwheelsSource,
    }

    async def get_package_info(
        self,
        package: str,
        *,
        include_prerelease: bool = False,
        source: str | None = None,
        fallback: bool = True,
    ) -> PackageInfo:
        if not PYPI_PACKAGE_PATTERN.match(package):
            raise InvalidPackageNameError(f"Invalid package name '{package}'. Use only a-zA-Z0-9_-")

        if source:
            source_class = self.SOURCE_MAP.get(source.lower())
            if not source_class:
                raise ValueError(f"Unknown source '{source}'. Available: {list(self.SOURCE_MAP.keys())}")
            sources = [source_class] + ([s for s in self.SOURCES if s != source_class] if fallback else [])
        else:
            sources = list(self.SOURCES) if fallback else [self.SOURCES[0]]

        last_error: Exception | None = None

        for source_class in sources:
            try:
                return await source_class().fetch(package, include_prerelease)
            except Exception as e:  # noqa: PERF203
                last_error = e
                if not fallback:
                    raise

        raise last_error or PackageNotFoundError(f"Failed to fetch package '{package}'")
