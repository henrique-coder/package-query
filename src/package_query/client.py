from __future__ import annotations

from asyncio import gather
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
        """Query a single package version from a registry.

        Args:
            registry: One of ``pypi``, ``npm``, ``crates``, ``docker``, ``github-actions``.
            package: Package name (e.g. ``"requests"``, ``"actions/checkout"``).
            include_prerelease: Include pre-release versions if True.
            source: Preferred source within the registry (e.g. ``"piwheels"`` for PyPI).
            fallback: Fall back to other sources on failure.

        Returns:
            A :class:`PackageInfo` with the resolved name, version and registry.
        """
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

    async def query_batch(
        self,
        packages: list[dict[str, str]],
        *,
        include_prerelease: bool = False,
    ) -> list[PackageInfo | Exception]:
        """Query multiple packages concurrently.

        Args:
            packages: List of dicts with ``"registry"`` and ``"package"`` keys.
                      Example: ``[{"registry": "pypi", "package": "requests"}, ...]``
            include_prerelease: Apply to all queries in the batch.

        Returns:
            A list matching the input order. Each entry is either a
            :class:`PackageInfo` on success or an :class:`Exception` on failure.
        """

        async def _safe_query(registry: str, package: str) -> PackageInfo | Exception:
            try:
                return await self.query(registry, package, include_prerelease=include_prerelease)
            except Exception as exc:
                return exc

        return list(await gather(*(_safe_query(item["registry"], item["package"]) for item in packages)))

    def format_batch(
        self,
        packages: list[dict[str, str]],
        results: list[PackageInfo | Exception],
    ) -> str:
        """Format batch results as a multi-line string in each registry's native format.

        Args:
            packages: The original input list (used to reconstruct error labels).
            results: The list returned by :meth:`query_batch`.

        Returns:
            One line per package. Success lines use the registry's native pinning
            format prefixed with ``[registry]``. Error lines show the registry and
            package name followed by the error message.

            Example output::

                [pypi] requests==2.32.3
                [npm] express@5.2.1
                [crates] serde = "=1.0.228"
                [docker] nginx:stable-alpine3.23
                [github-actions] actions/checkout@v4
                [pypi] error: Package 'nonexistent' not found on PyPI
        """
        lines: list[str] = []
        for item, result in zip(packages, results, strict=True):
            if isinstance(result, PackageInfo):
                lines.append(result.format_pinned())
            else:
                registry = item.get("registry", "unknown")
                package = item.get("package", "unknown")
                lines.append(f"[{registry}] {package}: error: {result}")
        return "\n".join(lines)

    def register(self, name: str, provider: type) -> None:
        """Register a custom provider under a new registry name."""
        self.REGISTRIES[name.lower()] = provider
