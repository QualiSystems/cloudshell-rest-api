from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path
from typing.io import BinaryIO
from urllib.parse import urljoin

import requests
from attrs import define, field
from typing_extensions import Self

from cloudshell.rest.exceptions import (
    FeatureUnavailable,
    LoginFailedError,
    PackagingRestApiError,
    ShellNotFound,
)
from cloudshell.rest.models import ShellInfo, StandardInfo
from cloudshell.rest.progress_bar import iter_resp_with_pb, upload_with_pb

DEFAULT_API_TIMEOUT = 15


@define
class PackagingRestApiClient:
    host: str
    _token: str = field(repr=False)
    port: int = 9000
    _show_progress: bool = field(default=False, repr=False)
    _api_timeout: int = field(default=DEFAULT_API_TIMEOUT, repr=False)
    _api_url: str = field(init=False)
    _headers: dict[str, str] = field(init=False)

    def __attrs_post_init__(self):
        self._api_url = _get_api_url(self.host, self.port)
        self._headers = {"Authorization": f"Basic {self._token}"}

    @classmethod
    def login(
        cls,
        host: str,
        username: str,
        password: str,
        domain: str = "Global",
        port: int = 9000,
        show_progress: bool = False,
        api_timeout: int = DEFAULT_API_TIMEOUT,
    ) -> Self:
        url = urljoin(_get_api_url(host, port), "Auth/Login")
        req_data = {
            "username": username,
            "password": password,
            "domain": domain,
        }
        resp = requests.put(url, data=req_data, timeout=api_timeout)
        if resp.status_code == 401:
            raise LoginFailedError(resp.text)
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)
        token = resp.text.strip("'\"")
        return cls(
            host, token, port, show_progress=show_progress, api_timeout=api_timeout
        )

    def add_shell_from_buffer(self, file_obj: BinaryIO | bytes) -> None:
        """Add a new Shell from the buffer or binary."""
        url = urljoin(self._api_url, "Shells")
        req_data = {"files": ("file", file_obj)}
        headers = self._headers.copy()

        with upload_with_pb(req_data, headers, show=self._show_progress) as new_data:
            resp = requests.post(
                url, data=new_data, headers=headers, timeout=self._api_timeout
            )

        if resp.status_code != 201:
            msg = f"Can't add shell, response: {resp.text}"
            raise PackagingRestApiError(msg)

    def add_shell(self, shell_path: str | Path) -> None:
        """Adds a new Shell Entity to CloudShell.

        If the shell exists, exception will be thrown
        """
        with open(shell_path, "rb") as f:
            self.add_shell_from_buffer(f)

    def update_shell_from_buffer(
        self, file_obj: BinaryIO | bytes, shell_name: str
    ) -> None:
        """Updates an existing Shell from the buffer or binary."""
        url = urljoin(self._api_url, f"Shells/{shell_name}")
        req_data = {"files": ("file", file_obj)}
        headers = self._headers.copy()

        with upload_with_pb(req_data, headers, show=self._show_progress) as new_data:
            resp = requests.put(
                url, data=new_data, headers=headers, timeout=self._api_timeout
            )

        if resp.status_code == 404:
            raise ShellNotFound()
        elif resp.status_code != 200:
            msg = f"Can't update shell, response: {resp.text}"
            raise PackagingRestApiError(msg)

    def update_shell(
        self, shell_path: str | Path, shell_name: str | None = None
    ) -> None:
        """Updates an existing Shell Entity in CloudShell."""
        shell_name = shell_name or os.path.basename(shell_path).rsplit(".", 1)[0]
        with open(shell_path, "rb") as f:
            self.update_shell_from_buffer(f, shell_name)

    def get_installed_standards(self) -> list[dict]:
        """Gets all standards installed on CloudShell."""
        url = urljoin(self._api_url, "Standards")
        resp = requests.get(url, headers=self._headers, timeout=self._api_timeout)
        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)
        return resp.json()

    def get_installed_standards_as_models(self) -> list[StandardInfo]:
        """Get all standards installed on CloudShell as models."""
        return [StandardInfo.from_dict(s) for s in self.get_installed_standards()]

    def get_shell(self, shell_name: str) -> dict:
        """Get a Shell's information."""
        url = urljoin(self._api_url, f"Shells/{shell_name}")
        resp = requests.get(url, headers=self._headers, timeout=self._api_timeout)
        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code == 400:
            raise ShellNotFound()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)
        return resp.json()

    def get_shell_as_model(self, shell_name: str) -> ShellInfo:
        """Get a Shell's information as model."""
        return ShellInfo.from_dict(self.get_shell(shell_name))

    def delete_shell(self, shell_name: str) -> None:
        """Delete a Shell from the CloudShell."""
        url = urljoin(self._api_url, f"Shells/{shell_name}")
        resp = requests.delete(url, headers=self._headers, timeout=self._api_timeout)
        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code == 400:
            raise ShellNotFound()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)

    def export_package(self, topologies: list[str]) -> Generator[bytes, None, None]:
        """Export a package with the topologies from the CloudShell."""
        url = urljoin(self._api_url, "Package/ExportPackage")
        req_data = {"TopologyNames": topologies}
        resp = requests.post(
            url,
            headers=self._headers,
            json=req_data,
            stream=True,
            timeout=self._api_timeout,
        )

        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)

        yield from iter_resp_with_pb(resp, show=self._show_progress)

    def export_package_to_file(
        self, topologies: list[str], file_path: str | Path
    ) -> None:
        """Export a package with the topologies and save it to the file."""
        with open(file_path, "wb") as f:
            for data in self.export_package(topologies):
                f.write(data)

    def import_package_from_buffer(self, file_obj: BinaryIO | bytes) -> None:
        """Import the package from buffer to the CloudShell."""
        url = urljoin(self._api_url, "Package/ImportPackage")
        req_data = {"files": ("file", file_obj)}
        headers = self._headers.copy()

        with upload_with_pb(req_data, headers, show=self._show_progress) as new_data:
            resp = requests.post(
                url, data=new_data, headers=headers, timeout=self._api_timeout
            )

        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)

    def import_package(self, package_path: str | Path) -> None:
        """Import the package from the file to the CloudShell."""
        with open(package_path, "rb") as f:
            self.import_package_from_buffer(f)


def _get_api_url(host: str, port: int) -> str:
    return f"http://{host}:{port}/API/"
