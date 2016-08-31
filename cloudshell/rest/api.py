import os
import re
import urllib2
from requests import post

from cloudshell.rest.exceptions import ShellNotFoundException


class CloudShellRestApiClient(object):
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
            .format(username, CloudShellRestApiClient._urlencode(password), domain)
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

    def update_shell(self, shell_path):
        """
        Updates an existing Shell Entity in CloudShell
        :param shell_path:
        :return:
        """
        filename = os.path.basename(shell_path)
        shell_name = os.path.splitext(filename)[0]
        url = 'http://{0}:{1}/API/Shells/{2}'.format(self.ip, self.port, shell_name)
        response = post(url,
                        files={filename: open(shell_path, 'rb')},
                        headers={'Authorization': 'Basic ' + self.token})

        if response.status_code == 404:  # Not Found
            raise ShellNotFoundException()

        if response.status_code != 200:  # Ok
            raise Exception(response.text)

    @staticmethod
    def _urlencode(s):
        return s.replace('+', '%2B').replace('/', '%2F').replace('=', '%3D')
