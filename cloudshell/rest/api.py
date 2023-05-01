from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing.io import BinaryIO
from urllib.parse import urljoin

import requests
from cached_property import cached_property

from cloudshell.rest.exceptions import (
    FeatureUnavailable,
    LoginFailedError,
    PackagingRestApiError,
    ShellNotFoundException,
)
from cloudshell.rest.models import ShellInfo, StandardInfo


class PackagingRestApiClient:
    def __init__(self, ip: str, port: int, username: str, password: str, domain: str):
        """Initialize REST API handler.

        :param ip: CloudShell server IP or host name
        :param port: port, usually 9000
        :param username: CloudShell username
        :param password: CloudShell password
        :param domain: CloudShell domain, usually Global
        """
        self.ip = ip
        self.port = port
        self._api_url = f"http://{ip}:{port}/API/"
        self._username = username
        self._password = password
        self._domain = domain

    @cached_property
    def _token(self) -> str:
        return self._get_token()

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Basic {self._token}"}

    def _get_token(self) -> str:
        url = urljoin(self._api_url, "Auth/Login")
        req_data = {
            "username": self._username,
            "password": self._password,
            "domain": self._domain,
        }
        resp = requests.put(url, data=req_data)
        if resp.status_code == 401:
            raise LoginFailedError(
                resp.url, resp.status_code, resp.text, resp.headers, None
            )
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)
        token = resp.text
        return token.strip("'\"")

    def add_shell_from_buffer(self, file_obj: BinaryIO | bytes) -> None:
        """Add a new Shell from the buffer or binary."""
        url = urljoin(self._api_url, "Shells")
        req_data = {"file": file_obj}
        resp = requests.post(url, files=req_data, headers=self._headers)
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
        req_data = {"file": file_obj}
        resp = requests.put(url, files=req_data, headers=self._headers)
        if resp.status_code == 404:
            raise ShellNotFoundException()
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
        resp = requests.get(url, headers=self._headers)
        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)
        return resp.json()

    def get_installed_standards_as_models(self) -> list[StandardInfo]:
        """Get all standards installed on CloudShell as models."""
        return [StandardInfo(s) for s in self.get_installed_standards()]

    def get_shell(self, shell_name: str) -> dict:
        """Get a Shell's information."""
        url = urljoin(self._api_url, f"Shells/{shell_name}")
        resp = requests.get(url, headers=self._headers)
        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code == 400:
            raise ShellNotFoundException()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)
        return resp.json()

    def get_shell_as_model(self, shell_name: str) -> ShellInfo:
        """Get a Shell's information as model."""
        return ShellInfo(self.get_shell(shell_name))

    def delete_shell(self, shell_name: str) -> None:
        """Delete a Shell from the CloudShell."""
        url = urljoin(self._api_url, f"Shells/{shell_name}")
        resp = requests.delete(url, headers=self._headers)
        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code == 400:
            raise ShellNotFoundException()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)

    def export_package(self, topologies: list[str]) -> bytes:
        """Export a package with the topologies from the CloudShell."""
        url = urljoin(self._api_url, "Package/ExportPackage")
        req_data = {"TopologyNames": topologies}
        resp = requests.post(url, headers=self._headers, json=req_data)
        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)
        return resp.content

    def export_package_to_file(
        self, topologies: list[str], file_path: str | Path
    ) -> None:
        """Export a package with the topologies and save it to the file."""
        with open(file_path, "wb") as f:
            f.write(self.export_package(topologies))

    def import_package_from_buffer(self, file_obj: BinaryIO | bytes) -> None:
        """Import the package from buffer to the CloudShell."""
        url = urljoin(self._api_url, "Package/ImportPackage")
        req_data = {"file": file_obj}
        resp = requests.post(url, headers=self._headers, files=req_data)
        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)

    def import_package(self, package_path: str | Path) -> None:
        """Import the package from the file to the CloudShell."""
        with open(package_path, "rb") as f:
            self.import_package_from_buffer(f)

    def upload_environment_zip_data(self, zipdata):
        warnings.warn(
            "This method is deprecated, use import_package_from_buffer instead",
            DeprecationWarning,
        )
        self.import_package_from_buffer(zipdata)

    def upload_environment_zip_file(self, zipfilename):
        warnings.warn(
            "This method is deprecated, use import_package instead", DeprecationWarning
        )
        self.import_package(zipfilename)
