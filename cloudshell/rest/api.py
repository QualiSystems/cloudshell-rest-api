import os

import requests
from cached_property import cached_property

from cloudshell.rest.exceptions import (
    FeatureUnavailable,
    PackagingRestApiError,
    ShellNotFoundException,
)

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin


class PackagingRestApiClient(object):
    def __init__(self, ip, port, username, password, domain):
        """Initialize REST API handler.

        :param ip: CloudShell server IP or host name
        :param port: port, usually 9000
        :param username: CloudShell username
        :param password: CloudShell password
        :param domain: CloudShell domain, usually Global
        """
        self.ip = ip
        self.port = port
        self._api_url = "http://{ip}:{port}/API/".format(**locals())
        self._username = username
        self._password = password
        self._domain = domain

    @cached_property
    def _token(self):
        return self._get_token()

    @property
    def _headers(self):
        return {"Authorization": "Basic {}".format(self._token)}

    def _get_token(self):
        url = urljoin(self._api_url, "Auth/Login")
        req_data = {
            "username": self._username,
            "password": self._password,
            "domain": self._domain,
        }
        resp = requests.put(url, data=req_data)
        token = resp.text
        return token.strip("'\"")

    def add_shell_from_buffer(self, file_obj):
        """Add a new Shell from the buffer or binary.

        :type file_obj: io.BinaryIO|bytes
        """
        url = urljoin(self._api_url, "Shells")
        req_data = {"file": file_obj}
        resp = requests.post(url, files=req_data, headers=self._headers)
        if resp.status_code != 201:
            msg = "Can't add shell, response: {}".format(resp.text)
            raise PackagingRestApiError(msg)

    def add_shell(self, shell_path):
        """Adds a new Shell Entity to CloudShell.

        If the shell exists, exception will be thrown
        :type shell_path: str
        """
        with open(shell_path, "rb") as f:
            self.add_shell_from_buffer(f)

    def update_shell_from_buffer(self, file_obj, shell_name):
        """Updates an existing Shell from the buffer or binary.

        :type file_obj: io.BinaryIO|bytes
        :type shell_name: str
        """
        url = urljoin(self._api_url, "Shells/{}".format(shell_name))
        req_data = {"file": file_obj}
        resp = requests.put(url, files=req_data, headers=self._headers)
        if resp.status_code == 404:
            raise ShellNotFoundException()
        elif resp.status_code != 200:
            msg = "Can't update shell, response: {}".format(resp.text)
            raise PackagingRestApiError(msg)

    def update_shell(self, shell_path, shell_name=None):
        """Updates an existing Shell Entity in CloudShell.

        :type shell_path: str
        :type shell_name: str
        """
        shell_name = shell_name or os.path.basename(shell_path).rsplit(".", 1)[0]
        with open(shell_path, "rb") as f:
            self.update_shell_from_buffer(f, shell_name)

    def get_installed_standards(self):
        """Gets all standards installed on CloudShell.

        :rtype: dict
        """
        url = urljoin(self._api_url, "Standards")
        resp = requests.get(url, headers=self._headers)
        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)
        return resp.json()

    def get_shell(self, shell_name):
        """Get a Shell's information."""
        url = urljoin(self._api_url, "Shells/{}".format(shell_name))
        resp = requests.get(url, headers=self._headers)
        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code == 400:
            raise ShellNotFoundException()
        return resp.json()

    def delete_shell(self, shell_name):
        """Delete a Shell from the CloudShell."""
        url = urljoin(self._api_url, "Shells/{}".format(shell_name))
        resp = requests.delete(url, headers=self._headers)
        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code == 400:
            raise ShellNotFoundException()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)

    def export_package(self, topologies):
        """Export a package with the topologies from the CloudShell.

        :type topologies: list[str]
        :rtype: bytes
        :return: package content
        """
        url = urljoin(self._api_url, "Package/ExportPackage")
        req_data = {"TopologyNames": topologies}
        resp = requests.post(url, headers=self._headers, json=req_data)
        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)
        return resp.content

    def export_package_to_file(self, topologies, file_path):
        """Export a package with the topologies and save it to the file.

        :type topologies: list[str]
        :type file_path: str
        """
        with open(file_path, "wb") as f:
            f.write(self.export_package(topologies))

    def import_package_from_buffer(self, file_obj):
        """Import the package from buffer to the CloudShell.

        :type file_obj: io.BinaryIO|bytes
        """
        url = urljoin(self._api_url, "Package/ImportPackage")
        req_data = {"file": file_obj}
        resp = requests.post(url, headers=self._headers, files=req_data)
        if resp.status_code == 404:
            raise FeatureUnavailable()
        elif resp.status_code != 200:
            raise PackagingRestApiError(resp.text)

    def import_package(self, package_path):
        """Import the package from the file to the CloudShell.

        :type package_path: str
        """
        with open(package_path, "rb") as f:
            self.import_package_from_buffer(f)
