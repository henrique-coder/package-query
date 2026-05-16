from __future__ import annotations

from typing import Final

from package_query.constants import CRATES_API_URL, CRATES_PACKAGE_PATTERN, HTTP_HEADERS
from package_query.exceptions import InvalidPackageNameError, PackageNotFoundError
from package_query.http import fetch_json
from package_query.models import PackageInfo


class CratesProvider:
    REGISTRY_NAME: Final[str] = "crates"

    async def get_package_info(
        self,
        package: str,
        *,
        include_prerelease: bool = False,
        source: str | None = None,
        fallback: bool = True,
    ) -> PackageInfo:
        if not CRATES_PACKAGE_PATTERN.match(package):
            raise InvalidPackageNameError(f"Invalid crate name '{package}'")

        url: str = f"{CRATES_API_URL}/{package}"

        try:
            data: dict = await fetch_json(url, HTTP_HEADERS)
        except PackageNotFoundError:
            raise PackageNotFoundError(f"Crate '{package}' not found on crates.io") from None

        crate: dict = data.get("crate", {})
        versions: list[dict] = data.get("versions", [])

        version: str = crate.get("max_stable_version") or crate.get("max_version", "")
        is_prerelease: bool = False

        if include_prerelease and versions:
            version = versions[0].get("num", version)
            is_prerelease = versions[0].get("yanked", False)

        return PackageInfo(
            name=crate.get("name", package),
            version=version,
            registry=self.REGISTRY_NAME,
            is_prerelease=is_prerelease,
        )
