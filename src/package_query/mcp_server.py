"""
MCP Server for package-query.

Exposes package version queries to AI agents via Model Context Protocol.
"""

from __future__ import annotations

from fastmcp import FastMCP

from package_query import PackageQuery


mcp = FastMCP(
    name="package-query",
    instructions=(
        "Query latest package versions from PyPI, npm, crates.io, Docker Hub, and GitHub Actions. "
        "Use get_package_version for a single package, or get_package_versions for multiple packages "
        "at once (recommended to reduce round-trips). Results include the registry name and use each "
        "ecosystem's native version-pinning format so they can be pasted directly into config files."
    ),
)


@mcp.tool()
async def get_package_version(
    registry: str,
    package: str,
    include_prerelease: bool = False,
) -> str:
    """Get the latest version of a single package from a registry.

    Returns a pinned version string in the registry's native format, prefixed
    with the registry name. Examples:

    - ``[pypi] requests==2.32.3``
    - ``[npm] express@5.2.1``
    - ``[crates] serde = "=1.0.228"``
    - ``[docker] nginx:stable-alpine3.23``
    - ``[github-actions] actions/checkout@v4``

    Args:
        registry: One of: pypi, npm, crates, docker, github-actions
        package: Package name (e.g. "requests", "express", "nginx", "actions/checkout")
        include_prerelease: Include pre-release versions if True (default: False)
    """
    pq = PackageQuery()
    info = await pq.query(registry, package, include_prerelease=include_prerelease)
    return info.format_pinned()


@mcp.tool()
async def get_package_versions(
    packages: list[dict[str, str]],
    include_prerelease: bool = False,
) -> str:
    """Get the latest versions of multiple packages in a single batch call.

    All queries are executed concurrently for maximum speed. Results are
    returned as one line per package in each registry's native pinning format,
    prefixed with the registry name so packages with the same name across
    different registries can be distinguished.

    Args:
        packages: List of objects, each with ``"registry"`` and ``"package"`` keys.
            Supported registries: ``pypi``, ``npm``, ``crates``, ``docker``, ``github-actions``.

            Example input::

                [
                    {"registry": "pypi", "package": "requests"},
                    {"registry": "pypi", "package": "flask"},
                    {"registry": "npm", "package": "express"},
                    {"registry": "crates", "package": "serde"},
                    {"registry": "docker", "package": "nginx"},
                    {"registry": "github-actions", "package": "actions/checkout"},
                ]

        include_prerelease: Include pre-release versions for all queries (default: False)

    Returns:
        Multi-line string — one entry per package::

            [pypi] requests==2.32.3
            [pypi] flask==3.1.1
            [npm] express@5.2.1
            [crates] serde = "=1.0.228"
            [docker] nginx:stable-alpine3.23
            [github-actions] actions/checkout@v4

        Failed entries look like::

            [pypi] nonexistent: error: Package 'nonexistent' not found on PyPI
    """
    pq = PackageQuery()
    results = await pq.query_batch(packages, include_prerelease=include_prerelease)
    return pq.format_batch(packages, results)


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
