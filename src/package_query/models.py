from typing import Any

from pydantic import BaseModel


class PackageInfo(BaseModel):
    name: str
    version: str
    summary: str | None = None
    released_at: str | None = None
    is_prerelease: bool = False
    homepage_url: str | None = None
    registry_url: str | None = None
    registry: str | None = None
    source_used: str | None = None
    sources_failed: list[str] = []
    sources_remaining: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
