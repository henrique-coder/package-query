from typing import Final

from package_query.constants import (
    GITHUB_API_BASE_URL,
    GITHUB_HEADERS,
    GITHUB_REPO_PATTERN,
    MAJOR_VERSION_PATTERN,
    SEMVER_PATTERN,
)
from package_query.http import fetch_json
from package_query.models import PackageInfo


class GitHubActionsProvider:
    REGISTRY_NAME: Final[str] = "github-actions"
    SOURCE_NAME: Final[str] = "github-api"

    async def get_package_info(
        self,
        package: str,
        *,
        include_prerelease: bool = False,
        source: str | None = None,
        fallback: bool = True,
    ) -> PackageInfo:
        if not GITHUB_REPO_PATTERN.match(package):
            raise ValueError(f"Invalid action format '{package}'. Expected 'owner/repo'")

        owner, repo = package.split("/", 1)
        tags_url: str = f"{GITHUB_API_BASE_URL}/{owner}/{repo}/tags"

        try:
            tags: list[dict] = await fetch_json(tags_url, GITHUB_HEADERS)
        except ValueError as e:
            if str(e) == "Not found":
                raise ValueError(f"Action '{package}' not found") from e
            raise

        if not tags:
            raise ValueError(f"Action '{package}' has no tags")

        major_versions: dict[int, str] = {}
        latest_semver: tuple[int, int, int] | None = None
        latest_semver_tag: str | None = None

        for tag in tags:
            name: str = tag.get("name", "")
            if major_match := MAJOR_VERSION_PATTERN.match(name):
                major_num: int = int(major_match.group(1))
                if major_num not in major_versions:
                    major_versions[major_num] = name
            elif semver_match := SEMVER_PATTERN.match(name):
                version_tuple: tuple[int, int, int] = (
                    int(semver_match.group(1)),
                    int(semver_match.group(2)),
                    int(semver_match.group(3)),
                )
                if latest_semver is None or version_tuple > latest_semver:
                    latest_semver, latest_semver_tag = version_tuple, name

        if major_versions:
            version: str = major_versions[max(major_versions.keys())]
        elif latest_semver_tag:
            version = latest_semver_tag
        else:
            version = tags[0].get("name", "unknown")

        return PackageInfo(
            name=package,
            version=version,
            is_prerelease=False,
            registry=self.REGISTRY_NAME,
            source_used=self.SOURCE_NAME,
        )
