from typing import Protocol

from package_query.models import PackageInfo


class PackageProvider(Protocol):
    async def get_package_info(self, package: str) -> PackageInfo: ...
