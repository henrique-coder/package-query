from typing import Final

from package_query.models import PackageInfo
from package_query.providers.crates import CratesProvider
from package_query.providers.dockerhub import DockerHubProvider
from package_query.providers.github_actions import GitHubActionsProvider
from package_query.providers.npm import NpmProvider
from package_query.providers.pypi import PyPIProvider


class PackageQuery:
    REGISTRIES: Final[dict[str, type]] = {
        "pypi": PyPIProvider,
        "github-actions": GitHubActionsProvider,
        "npm": NpmProvider,
        "crates": CratesProvider,
        "docker": DockerHubProvider,
    }

    async def query(
        self,
        registry: str,
        package: str,
        *,
        include_prerelease: bool = False,
        source: str | None = None,
        fallback: bool = True,
    ) -> PackageInfo:
        provider_class = self.REGISTRIES.get(registry.lower())
        if provider_class is None:
            supported: str = ", ".join(self.REGISTRIES.keys())
            raise ValueError(f"Unsupported registry '{registry}'. Supported: {supported}")
        return await provider_class().get_package_info(
            package,
            include_prerelease=include_prerelease,
            source=source,
            fallback=fallback,
        )

    def register(self, name: str, provider: type) -> None:
        self.REGISTRIES[name.lower()] = provider
