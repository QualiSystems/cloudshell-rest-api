from pathlib import Path
from typing import BinaryIO, List, Optional, Union
from urllib.parse import urljoin

import aiofiles
import aiohttp
from aiohttp import ClientSession
from async_property import async_cached_property

from cloudshell.rest.exceptions import (
    FeatureUnavailable,
    PackagingRestApiError,
    ShellNotFoundException,
)


class AsyncPackagingRestApiClient:
    DEFAULT_DOMAIN = "Global"
    DEFAULT_PORT = 9000

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        domain: str = DEFAULT_DOMAIN,
        port: int = DEFAULT_PORT,
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._domain = domain
        self._api_url = f"http://{host}:{port}/API/"

    @async_cached_property
    async def _token(self) -> str:
        return await self._get_token()

    async def _get_token(self):
        url = urljoin(self._api_url, "Auth/Login")
        req_data = {
            "username": self._username,
            "password": self._password,
            "domain": self._domain,
        }
        async with aiohttp.ClientSession() as session:
            async with session.put(url, data=req_data) as resp:
                token = await resp.text()
        return token.strip("'\"")

    async def _get_session(self) -> ClientSession:
        headers = {"Authorization": f"Basic {await self._token}"}
        return aiohttp.ClientSession(headers=headers)

    async def add_shell_from_buffer(self, file_obj: Union[BinaryIO, bytes]):
        url = urljoin(self._api_url, "Shells")
        req_data = {"file": file_obj}
        async with await self._get_session() as session:
            async with session.post(url, data=req_data) as resp:
                if resp.status != 201:
                    msg = f"Can't add shell, response: {await resp.text()}"
                    raise PackagingRestApiError(msg)

    async def add_shell(self, shell_path: Union[Path, str]):
        shell_path = Path(shell_path)
        async with aiofiles.open(shell_path, "rb") as f:
            await self.add_shell_from_buffer(await f.read())

    async def update_shell_from_buffer(
        self, file_obj: Union[BinaryIO, bytes], shell_name: str
    ):
        url = urljoin(self._api_url, f"Shells/{shell_name}")
        req_data = {"file": file_obj}
        async with await self._get_session() as session:
            async with session.put(url, data=req_data) as resp:
                if resp.status == 404:
                    raise ShellNotFoundException()
                elif resp.status != 200:
                    msg = f"Can't update shell, response: {await resp.text()}"
                    raise PackagingRestApiError(msg)

    async def update_shell(
        self, shell_path: Union[Path, str], shell_name: Optional[str] = None
    ):
        shell_path = Path(shell_path)
        shell_name = shell_name or shell_path.name.rsplit(".", 1)[0]
        async with aiofiles.open(shell_path, "rb") as f:
            await self.update_shell_from_buffer(await f.read(), shell_name)

    async def get_shell(self, shell_name: str) -> dict:
        url = urljoin(self._api_url, f"Shells/{shell_name}")
        async with await self._get_session() as session:
            async with session.get(url) as resp:
                if resp.status == 404:
                    raise FeatureUnavailable()
                elif resp.status == 400:
                    raise ShellNotFoundException()
                return await resp.json()

    async def delete_shell(self, shell_name: str):
        url = urljoin(self._api_url, f"Shells/{shell_name}")
        async with await self._get_session() as session:
            async with session.delete(url) as resp:
                if resp.status == 404:
                    raise FeatureUnavailable()
                elif resp.status == 400:
                    raise ShellNotFoundException()
                elif resp.status != 200:
                    raise PackagingRestApiError(await resp.text())

    async def get_installed_standards(self) -> list:
        url = urljoin(self._api_url, "Standards")
        async with await self._get_session() as session:
            async with session.get(url) as resp:
                if resp.status == 404:
                    raise FeatureUnavailable()
                elif resp.status != 200:
                    raise PackagingRestApiError(await resp.text())
                return await resp.json()

    async def export_package(self, topologies: List[str]) -> bytes:
        url = urljoin(self._api_url, "Package/ExportPackage")
        req_data = {"TopologyNames": topologies}
        async with await self._get_session() as session:
            async with session.post(url, json=req_data) as resp:
                if resp.status == 404:
                    raise FeatureUnavailable()
                elif resp.status != 200:
                    raise PackagingRestApiError(await resp.text())
                return await resp.read()

    async def export_package_to_file(
        self, topologies: List[str], file_path: Union[Path, str]
    ):
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await self.export_package(topologies))

    async def import_package_from_buffer(self, file_obj: Union[BinaryIO, bytes]):
        url = urljoin(self._api_url, "Package/ImportPackage")
        req_data = {"file": file_obj}
        async with await self._get_session() as session:
            async with session.post(url, data=req_data) as resp:
                if resp.status == 404:
                    raise FeatureUnavailable()
                elif resp.status != 200:
                    raise PackagingRestApiError(await resp.text())
                await resp.json()

    async def import_package(self, package_path: Union[Path, str]):
        async with aiofiles.open(package_path, "rb") as f:
            await self.import_package_from_buffer(await f.read())
