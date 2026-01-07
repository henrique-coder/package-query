from datetime import datetime
from typing import Any, Final

from curl_cffi.requests import AsyncSession
import orjson

from package_query.constants import HTTP_HEADERS, PYPI_PACKAGE_PATTERN
from package_query.models import PackageInfo


class PyPIPiwheelsSource:
    NAME: Final[str] = "piwheels"
    BASE_URL: Final[str] = "https://www.piwheels.org/project"

    async def fetch(self, package: str, include_prerelease: bool = False) -> PackageInfo:
        url: str = f"{self.BASE_URL}/{package}/json/"

        async with AsyncSession() as session:
            response = await session.get(url, headers=HTTP_HEADERS)

        if response.status_code == 404:
            raise ValueError(f"Package '{package}' not found")

        response.raise_for_status()
        data: dict = orjson.loads(response.content)
        releases: dict = data.get("releases", {})

        if not releases:
            raise ValueError(f"Package '{package}' has no releases")

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

            if include_prerelease or not version_is_prerelease:
                if latest_released is None or released > latest_released:
                    latest_version = version
                    latest_released = released
                    is_prerelease = version_is_prerelease

        if latest_version is None:
            raise ValueError(f"Package '{package}' has no valid releases")

        return PackageInfo(
            name=data.get("package", package),
            version=latest_version,
            summary=data.get("summary"),
            released_at=latest_released.strftime("%Y-%m-%dT%H:%M:%SZ") if latest_released else None,
            is_prerelease=is_prerelease,
            homepage_url=data.get("pypi_url"),
            registry_url=data.get("pypi_url"),
        )


class PyPIOfficialSource:
    NAME: Final[str] = "pypi"
    BASE_URL: Final[str] = "https://pypi.org/pypi"

    async def fetch(self, package: str, include_prerelease: bool = False) -> PackageInfo:
        url: str = f"{self.BASE_URL}/{package}/json"

        async with AsyncSession() as session:
            response = await session.get(url, headers=HTTP_HEADERS)

        if response.status_code == 404:
            raise ValueError(f"Package '{package}' not found")

        response.raise_for_status()
        data: dict = orjson.loads(response.content)

        info: dict = data.get("info", {})
        version: str = info.get("version", "")
        releases: dict[str, list[dict[str, Any]]] = data.get("releases", {})

        released_at: str | None = None
        if releases.get(version):
            upload_time: str | None = releases[version][0].get("upload_time_iso_8601")
            if upload_time:
                released_at = upload_time[:19] + "Z"

        return PackageInfo(
            name=info.get("name", package),
            version=version,
            summary=info.get("summary"),
            released_at=released_at,
            is_prerelease=False,
            homepage_url=info.get("project_url") or f"https://pypi.org/project/{package}",
            registry_url=f"https://pypi.org/project/{package}",
        )


class PyPIProvider:
    REGISTRY_NAME: Final[str] = "pypi"
    SOURCES: Final[list[type]] = [PyPIPiwheelsSource, PyPIOfficialSource]
    SOURCE_MAP: Final[dict[str, type]] = {
        "piwheels": PyPIPiwheelsSource,
        "pypi": PyPIOfficialSource,
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
            raise ValueError(f"Invalid package name '{package}'. Use only a-zA-Z0-9_-")

        if source:
            source_class = self.SOURCE_MAP.get(source.lower())
            if not source_class:
                raise ValueError(f"Unknown source '{source}'. Available: {list(self.SOURCE_MAP.keys())}")
            sources = [source_class] + ([s for s in self.SOURCES if s != source_class] if fallback else [])
        else:
            sources = list(self.SOURCES) if fallback else [self.SOURCES[0]]

        sources_failed: list[str] = []
        last_error: Exception | None = None

        for i, source_class in enumerate(sources):
            try:
                result: PackageInfo = await source_class().fetch(package, include_prerelease)
                result.registry = self.REGISTRY_NAME
                result.source_used = source_class.NAME
                result.sources_failed = sources_failed
                result.sources_remaining = [s.NAME for s in sources[i + 1 :]]
                return result
            except Exception as e:
                sources_failed.append(source_class.NAME)
                last_error = e
                if not fallback:
                    raise

        raise last_error or ValueError(f"Failed to fetch package '{package}'")
