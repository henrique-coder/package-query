"""
MCP Server for package-query.

Exposes package version queries to AI agents via Model Context Protocol.
"""

from fastmcp import FastMCP

from package_query import PackageQuery


mcp = FastMCP(
    "package-query",
    "Query latest package versions from PyPI, npm, crates.io, Docker Hub, and GitHub Actions",
)


@mcp.tool()
async def get_package_version(
    registry: str,
    package: str,
    include_prerelease: bool = False,
) -> str:
    """
    Get the latest version of a package from a registry.

    Args:
        registry: One of: pypi, npm, crates, docker, github-actions
        package: Package name (e.g. "requests", "express", "nginx", "actions/checkout")
        include_prerelease: Include pre-release versions if True (default: False)

    Returns:
        A formatted string with package name, version, and registry URL
    """
    pq = PackageQuery()
    info = await pq.query(registry, package, include_prerelease=include_prerelease)
    return f"{info.name}=={info.version} ({info.registry_url})"


def main() -> None:
    """
    Entry point for the MCP server.
    """
    mcp.run()


if __name__ == "__main__":
    main()
