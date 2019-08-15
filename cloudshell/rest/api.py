#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json
try:
    import urllib2
except:
    import urllib.request as urllib2
from requests import delete, get, post, put

from cloudshell.rest.exceptions import ShellNotFoundException, FeatureUnavailable


class PackagingRestApiClient(object):
    def __init__(self, ip, port, username, password, domain):
        """
        Logs into CloudShell using REST API
        :param ip: CloudShell server IP or host name
        :param port: port, usually 9000
        :param username: CloudShell username
        :param password: CloudShell password
        :param domain: CloudShell domain, usually Global
        """
        self.ip = ip
        self.port = port
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        url = "http://{0}:{1}/API/Auth/Login".format(ip, port)
        data = "username={0}&password={1}&domain={2}" \
            .format(username, PackagingRestApiClient._urlencode(password), domain).encode()
        request = urllib2.Request(url=url, data=data)
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
        backup = request.get_method
        request.get_method = lambda: "PUT"
        url = opener.open(request)
        self.token = url.read()
        if isinstance(self.token, bytes):
            self.token = self.token.decode()

        self.token = self.token.strip("\"")
        request.get_method = backup

    def add_shell(self, shell_path):
        """
        Adds a new Shell Entity to CloudShell
        If the shell exists, exception will be thrown
        :param shell_path:
        :return:
        """
        url = "http://{0}:{1}/API/Shells".format(self.ip, self.port)
        response = post(url,
                        files={os.path.basename(shell_path): open(shell_path, "rb")},
                        headers={"Authorization": "Basic " + self.token})

        if response.status_code != 201:
            raise Exception(response.text)

    def update_shell(self, shell_path, shell_name=None):
        """
        Updates an existing Shell Entity in CloudShell
        :param shell_path: The path to the shell file
        :param shell_name: The shell name. if not supplied the shell name is derived from the shell path
        :return:
        """
        filename = os.path.basename(shell_path)
        shell_name = shell_name or self._get_shell_name_from_filename(filename)
        url = "http://{0}:{1}/API/Shells/{2}".format(self.ip, self.port, shell_name)
        response = put(url,
                       files={filename: open(shell_path, "rb")},
                       headers={"Authorization": "Basic " + self.token})

        if response.status_code == 404:  # Not Found
            raise ShellNotFoundException()

        if response.status_code != 200:  # Ok
            raise Exception(response.text)

    def get_installed_standards(self):
        """
        Gets all standards installed on CloudShell
        :return:
        """
        url = "http://{0}:{1}/API/Standards".format(self.ip, self.port)
        response = get(url,
                       headers={"Authorization": "Basic " + self.token})

        if response.status_code == 404:  # Feature unavailable (probably due to cloudshell version below 8.1)
            raise FeatureUnavailable()

        if response.status_code != 200:  # Ok
            raise Exception(response.text)

        return response.json()

    def get_shell(self, shell_name):
        url = "http://{0}:{1}/API/Shells/{2}".format(self.ip, self.port, shell_name)
        response = get(url,
                       headers={"Authorization": "Basic " + self.token})

        if response.status_code == 404 or response.status_code == 405:  # Feature unavailable (probably due to cloudshell version below 8.2)
            raise FeatureUnavailable()

        if response.status_code == 400:  # means shell not found
            raise ShellNotFoundException()

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    def delete_shell(self, shell_name):
        url = "http://{0}:{1}/API/Shells/{2}".format(self.ip, self.port, shell_name)
        response = delete(url,
                          headers={"Authorization": "Basic " + self.token})

        if response.status_code == 404 or response.status_code == 405:  # Feature unavailable (probably due to cloudshell version below 9.2)
            raise FeatureUnavailable()

        if response.status_code == 400:  # means shell not found
            raise ShellNotFoundException()

        if response.status_code != 200:
            raise Exception(response.text)

    def export_package(self, topologies):
        """Export a package with the topologies from the CloudShell

        :type topologies: list[str]
        :rtype: str
        :return: package content
        """
        url = "http://{0.ip}:{0.port}/API/Package/ExportPackage".format(self)
        response = post(
            url,
            headers={"Authorization": "Basic " + self.token},
            data={"TopologyNames": topologies},
        )

        if response.status_code in (404, 405):
            raise FeatureUnavailable()

        if not response.ok:
            raise Exception(response.text)

        return response.content

    def import_package(self, package_path):
        """Import the package to the CloudShell

        :type package_path: str
        """
        url = "http://{0.ip}:{0.port}/API/Package/ImportPackage".format(self)

        with open(package_path, "rb") as fo:
            response = post(
                url,
                headers={"Authorization": "Basic " + self.token},
                files={"file": fo},
            )

        if response.status_code in (404, 405):
            raise FeatureUnavailable()

        if not response.ok:
            raise Exception(response.text)

        if not response.json().get("Success"):
            error_msg = response.json().get("ErrorMessage", "Problem with importing the package")
            raise Exception(error_msg)

    @staticmethod
    def _urlencode(s):
        return s.replace("+", "%2B").replace("/", "%2F").replace("=", "%3D")

    @staticmethod
    def _get_shell_name_from_filename(filename):
        return os.path.splitext(filename)[0]

    def upload_environment_zip_file(self, zipfilename):
        with open(zipfilename, "rb") as g:
            zipdata = g.read()
            self.upload_environment_zip_data(zipdata)

    def upload_environment_zip_data(self, zipdata):

        boundary = b'''------------------------652c70c071862fc2'''

        fd = b'''--''' + boundary + \
             b'''\r\nContent-Disposition: form-data; name="file"; filename="my_zip.zip"''' + \
             b'''\r\nContent-Type: application/octet-stream\r\n\r\n''' + zipdata + \
             b'''\r\n--''' + boundary + b'''--\r\n'''

        class FakeReader(object):
            def __init__(self, k):
                self.k = k
                self.offset = 0

            def read(self, blocksize):
                if self.offset >= len(self.k):
                    return None

                if self.offset + blocksize >= len(self.k):
                    rv = self.k[self.offset:]
                    self.offset = len(self.k)
                else:
                    rv = self.k[self.offset:self.offset+blocksize]
                    self.offset += blocksize
                return rv

        fdreader = FakeReader(fd)

        request = urllib2.Request("http://{}:{}/API/Package/ImportPackage".format(self.ip, str(self.port)),
                                  data=fdreader)
        backup = request.get_method
        request.get_method = lambda: "POST"
        request.add_header("Authorization", "Basic " + self.token)
        request.add_header("Content-Type", "multipart/form-data; boundary=" + boundary)
        request.add_header("Accept", "*/*")
        request.add_header("Content-Length", str(len(fd)))
        request.get_method = backup
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        url = opener.open(request)

        try:
            s = url.read()
            if isinstance(s, bytes):
                s = s.decode()
            o = json.loads(s)
            if "Success" not in o:
                raise Exception("'Success' value not found in Quali API response: " + str(o))
        except Exception as ue:
            raise Exception("Error extracting Quali API zip import result: " + str(ue))

        if not o["Success"]:
            raise Exception("Error uploading Quali API zip package: "+o["ErrorMessage"])
