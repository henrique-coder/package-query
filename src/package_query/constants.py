from re import Pattern, compile
from typing import Final


PYPI_PACKAGE_PATTERN: Final[Pattern[str]] = compile(r"^[a-zA-Z0-9_-]+$")
GITHUB_REPO_PATTERN: Final[Pattern[str]] = compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?/[a-zA-Z0-9._-]+$")
NPM_PACKAGE_PATTERN: Final[Pattern[str]] = compile(r"^(@[a-zA-Z0-9_-]+/)?[a-zA-Z0-9._-]+$")
CRATES_PACKAGE_PATTERN: Final[Pattern[str]] = compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
DOCKER_IMAGE_PATTERN: Final[Pattern[str]] = compile(r"^[a-z0-9_-]+(/[a-z0-9._-]+)?$")

PIWHEELS_BASE_URL: Final[str] = "https://www.piwheels.org/project"
PYPI_BASE_URL: Final[str] = "https://pypi.org/project"
GITHUB_API_BASE_URL: Final[str] = "https://api.github.com/repos"
GITHUB_BASE_URL: Final[str] = "https://github.com"
NPM_REGISTRY_URL: Final[str] = "https://registry.npmjs.org"
NPM_BASE_URL: Final[str] = "https://www.npmjs.com/package"
CRATES_API_URL: Final[str] = "https://crates.io/api/v1/crates"
CRATES_BASE_URL: Final[str] = "https://crates.io/crates"
DOCKERHUB_API_URL: Final[str] = "https://hub.docker.com/v2/repositories"
DOCKERHUB_BASE_URL: Final[str] = "https://hub.docker.com/r"

HTTP_HEADERS: Final[dict[str, str]] = {
    "User-Agent": "package-query/1.0",
    "Accept": "application/json",
}

GITHUB_HEADERS: Final[dict[str, str]] = {
    "User-Agent": "package-query/1.0",
    "Accept": "application/vnd.github+json",
}

MAJOR_VERSION_PATTERN: Final[Pattern[str]] = compile(r"^v(\d+)$")
SEMVER_PATTERN: Final[Pattern[str]] = compile(r"^v(\d+)\.(\d+)\.(\d+)$")
