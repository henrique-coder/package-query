from typing import Final

from package_query.constants import (
    CRATES_API_URL,
    CRATES_PACKAGE_PATTERN,
    HTTP_HEADERS,
)
from package_query.http import fetch_json
from package_query.models import PackageInfo


class CratesProvider:
    REGISTRY_NAME: Final[str] = "crates"
    SOURCE_NAME: Final[str] = "crates.io"

    async def get_package_info(
        self,
        package: str,
        *,
        include_prerelease: bool = False,
        source: str | None = None,
        fallback: bool = True,
    ) -> PackageInfo:
        if not CRATES_PACKAGE_PATTERN.match(package):
            raise ValueError(f"Invalid crate name '{package}'")

        url: str = f"{CRATES_API_URL}/{package}"
        data: dict = await fetch_json(url, HTTP_HEADERS)

        crate: dict = data.get("crate", {})
        versions: list[dict] = data.get("versions", [])

        version: str = crate.get("max_version", "")
        is_prerelease: bool = False

        for v in versions:
            if v.get("num") == version:
                is_prerelease = v.get("yanked", False)
                break

        if include_prerelease and versions:
            version = versions[0].get("num", version)

        return PackageInfo(
            name=crate.get("name", package),
            version=version,
            is_prerelease=is_prerelease,
            registry=self.REGISTRY_NAME,
            source_used=self.SOURCE_NAME,
        )
