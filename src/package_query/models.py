from pydantic import BaseModel


class PackageInfo(BaseModel):
    name: str
    version: str
    is_prerelease: bool = False
    registry: str | None = None
    source_used: str | None = None
