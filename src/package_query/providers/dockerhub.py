from typing import Final

from package_query.constants import (
    DOCKER_IMAGE_PATTERN,
    DOCKERHUB_API_URL,
    HTTP_HEADERS,
)
from package_query.http import fetch_json
from package_query.models import PackageInfo


class DockerHubProvider:
    REGISTRY_NAME: Final[str] = "docker"
    SOURCE_NAME: Final[str] = "dockerhub"

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
            raise ValueError(f"Invalid Docker image name '{package}'")

        namespace, repo = package.split("/", 1)
        tags_url: str = f"{DOCKERHUB_API_URL}/{namespace}/{repo}/tags?page_size=10"
        data: dict = await fetch_json(tags_url, HTTP_HEADERS)

        results: list[dict] = data.get("results", [])
        if not results:
            raise ValueError(f"Docker image '{package}' has no tags")

        latest_tag: dict | None = None
        for tag in results:
            if tag.get("name") == "latest":
                latest_tag = tag
                break

        if not latest_tag:
            latest_tag = results[0]

        version: str = latest_tag.get("name", "latest")
        display_name: str = repo if namespace == "library" else package

        return PackageInfo(
            name=display_name,
            version=version,
            is_prerelease=False,
            registry=self.REGISTRY_NAME,
            source_used=self.SOURCE_NAME,
        )
