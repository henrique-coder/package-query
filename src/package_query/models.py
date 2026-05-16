from __future__ import annotations

from pydantic import BaseModel


class PackageInfo(BaseModel):
    """Holds resolved package metadata for a single registry lookup."""

    name: str
    version: str
    registry: str
    is_prerelease: bool = False

    def format_pinned(self) -> str:
        """Return the version-pinned string in the registry's native format.

        Returns:
            A string in the ecosystem-standard pinning format, prefixed with
            the registry name in brackets. Examples:

            - ``[pypi] requests==2.32.3``
            - ``[npm] express@5.2.1``
            - ``[crates] serde = "=1.0.228"``
            - ``[docker] nginx:stable-alpine3.23``
            - ``[github-actions] actions/checkout@v4``
        """

        match self.registry:
            case "pypi":
                pinned = f"{self.name}=={self.version}"
            case "npm":
                pinned = f"{self.name}@{self.version}"
            case "crates":
                pinned = f'{self.name} = "={self.version}"'
            case "docker":
                pinned = f"{self.name}:{self.version}"
            case "github-actions":
                pinned = f"{self.name}@{self.version}"
            case _:
                pinned = f"{self.name}=={self.version}"

        return f"[{self.registry}] {pinned}"
