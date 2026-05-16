from __future__ import annotations

from typing import Final

from package_query.constants import DOCKER_IMAGE_PATTERN, DOCKERHUB_API_URL, HTTP_HEADERS
from package_query.exceptions import InvalidPackageNameError, PackageNotFoundError
from package_query.http import fetch_json
from package_query.models import PackageInfo


class DockerHubProvider:
    REGISTRY_NAME: Final[str] = "docker"

    async def get_package_info(
        self,
        package: str,
        *,
        include_prerelease: bool = False,
        source: str | None = None,
        fallback: bool = True,
    ) -> PackageInfo:
        if "/" not in package:
            package = f"library/{package}"

        if not DOCKER_IMAGE_PATTERN.match(package):
            raise InvalidPackageNameError(f"Invalid Docker image name '{package}'")

        namespace, repo = package.split("/", 1)
        tags_url: str = f"{DOCKERHUB_API_URL}/{namespace}/{repo}/tags?page_size=10"

        try:
            data: dict = await fetch_json(tags_url, HTTP_HEADERS)
        except PackageNotFoundError:
            raise PackageNotFoundError(f"Docker image '{package}' not found on Docker Hub") from None

        results: list[dict] = data.get("results", [])
        if not results:
            raise PackageNotFoundError(f"Docker image '{package}' has no tags")

        # Prefer a meaningful stable tag over 'latest'
        preferred_tag: dict | None = None
        latest_tag: dict | None = None

        for tag in results:
            tag_name: str = tag.get("name", "")
            if tag_name == "latest":
                latest_tag = tag
            elif preferred_tag is None and tag_name not in ("", "latest"):
                preferred_tag = tag

        chosen: dict = preferred_tag or latest_tag or results[0]
        version: str = chosen.get("name", "latest")
        display_name: str = repo if namespace == "library" else package

        return PackageInfo(
            name=display_name,
            version=version,
            registry=self.REGISTRY_NAME,
            is_prerelease=False,
        )
