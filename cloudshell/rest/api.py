import os
import re
import urllib2
from requests import post, put, get

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
        url = 'http://{0}:{1}/API/Auth/Login'.format(ip, port)
        data = 'username={0}&password={1}&domain={2}' \
            .format(username, PackagingRestApiClient._urlencode(password), domain)
        request = urllib2.Request(url=url, data=data)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        backup = request.get_method
        request.get_method = lambda: 'PUT'
        url = opener.open(request)
        self.token = url.read()
        self.token = re.sub(r'^"', '', self.token)
        self.token = re.sub(r'"$', '', self.token)
        request.get_method = backup

    def add_shell(self, shell_path):
        """
        Adds a new Shell Entity to CloudShell
        If the shell exists, exception will be thrown
        :param shell_path:
        :return:
        """
        url = 'http://{0}:{1}/API/Shells'.format(self.ip, self.port)
        response = post(url,
                        files={os.path.basename(shell_path): open(shell_path, 'rb')},
                        headers={'Authorization': 'Basic ' + self.token})

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
        url = 'http://{0}:{1}/API/Shells/{2}'.format(self.ip, self.port, shell_name)
        response = put(url,
                       files={filename: open(shell_path, 'rb')},
                       headers={'Authorization': 'Basic ' + self.token})

        if response.status_code == 404:  # Not Found
            raise ShellNotFoundException()

        if response.status_code != 200:  # Ok
            raise Exception(response.text)

    def get_installed_standards(self):
        """
        Gets all standards installed on CloudShell
        :return:
        """
        url = 'http://{0}:{1}/API/Standards'.format(self.ip, self.port)
        response = get(url,
                       headers={'Authorization': 'Basic ' + self.token})

        if response.status_code == 404:  # Feature unavailable (probably due to cloudshell version below 8.1)
            raise FeatureUnavailable()

        if response.status_code != 200:  # Ok
            raise Exception(response.text)

        return response.json()

    def get_shell(self, shell_name):
        url = 'http://{0}:{1}/API/Shells/{2}'.format(self.ip, self.port, shell_name)
        response = get(url,
                       headers={'Authorization': 'Basic ' + self.token})

        if response.status_code == 404:  # Feature unavailable (probably due to cloudshell version below 8.2)
            raise FeatureUnavailable()

        if response.status_code == 400:  # means shell not found
            raise ShellNotFoundException()

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()


    @staticmethod
    def _urlencode(s):
        return s.replace('+', '%2B').replace('/', '%2F').replace('=', '%3D')

    @staticmethod
    def _get_shell_name_from_filename(filename):
        return os.path.splitext(filename)[0]
