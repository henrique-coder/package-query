from typing import Final

from package_query.constants import (
    HTTP_HEADERS,
    NPM_PACKAGE_PATTERN,
    NPM_REGISTRY_URL,
)
from package_query.http import fetch_json
from package_query.models import PackageInfo


class NpmProvider:
    REGISTRY_NAME: Final[str] = "npm"
    SOURCE_NAME: Final[str] = "npmjs"

    async def get_package_info(
        self,
        package: str,
        *,
        include_prerelease: bool = False,
        source: str | None = None,
        fallback: bool = True,
    ) -> PackageInfo:
        if not NPM_PACKAGE_PATTERN.match(package):
            raise ValueError(f"Invalid npm package name '{package}'")

        url: str = f"{NPM_REGISTRY_URL}/{package}"
        data: dict = await fetch_json(url, HTTP_HEADERS)

        dist_tags: dict = data.get("dist-tags", {})
        version: str = dist_tags.get("latest", "")

        if include_prerelease and "next" in dist_tags:
            version = dist_tags["next"]

        return PackageInfo(
            name=data.get("name", package),
            version=version,
            is_prerelease="next" in dist_tags and version == dist_tags.get("next"),
            registry=self.REGISTRY_NAME,
            source_used=self.SOURCE_NAME,
        )
