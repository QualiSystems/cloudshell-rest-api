import io
import json
import re

import pytest
import responses

from cloudshell.rest.api import PackagingRestApiClient
from cloudshell.rest.exceptions import (
    FeatureUnavailable,
    PackagingRestApiError,
    ShellNotFoundException,
)

try:
    from urlparse import urljoin, parse_qs
except ImportError:
    from urllib.parse import urljoin, parse_qs


HOST = "host"
PORT = 9000
USERNAME = "username"
PASSWORD = "password"
DOMAIN = "Global"
TOKEN = "token"
API_URL = "http://{HOST}:{PORT}/API/".format(**locals())


@pytest.fixture
def rest_api_client():
    return PackagingRestApiClient(HOST, 9000, USERNAME, PASSWORD, DOMAIN)


@pytest.fixture
def mocked_responses():
    token = "token"
    url = urljoin(API_URL, "Auth/Login")
    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, url, body=token)
        yield rsps


def test_login(rest_api_client, mocked_responses):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    assert rest_api_client._get_token() == TOKEN
    assert len(mocked_responses.calls) == 1
    req = mocked_responses.calls[0].request
    body = "username={USERNAME}&domain={DOMAIN}&password={PASSWORD}".format(**globals())
    assert parse_qs(req.body) == parse_qs(body)


def test_get_installed_standards(rest_api_client, mocked_responses):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    standards = [
        {
            "StandardName": "cloudshell_firewall_standard",
            "Versions": ["3.0.0", "3.0.1", "3.0.2"],
        },
        {
            "StandardName": "cloudshell_networking_standard",
            "Versions": ["5.0.0", "5.0.1", "5.0.2", "5.0.3", "5.0.4"],
        },
    ]
    url = urljoin(API_URL, "Standards")
    mocked_responses.add(responses.GET, url, json=standards)

    assert rest_api_client.get_installed_standards() == standards


@pytest.mark.parametrize(
    ("status_code", "text_msg", "expected_err_class", "expected_err_text"),
    (
        (404, "", FeatureUnavailable, ""),
        (500, "Internal server error", PackagingRestApiError, "Internal server error"),
    ),
)
def test_get_installed_standards_failed(
    status_code,
    text_msg,
    expected_err_class,
    expected_err_text,
    rest_api_client,
    mocked_responses,
):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    url = urljoin(API_URL, "Standards")
    mocked_responses.add(responses.GET, url, status=status_code, body=text_msg)

    with pytest.raises(expected_err_class, match=expected_err_text):
        rest_api_client.get_installed_standards()


def test_add_shell_from_buffer(rest_api_client, mocked_responses):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    url = urljoin(API_URL, "Shells")
    mocked_responses.add(responses.POST, url, status=201)

    file_content = b"test buffer"
    buffer = io.BytesIO(file_content)
    rest_api_client.add_shell_from_buffer(buffer)

    assert len(mocked_responses.calls) == 2
    body = mocked_responses.calls[1].request.body
    assert re.search(b'filename=["\']file["\']', body)
    pattern = b"\\s" + file_content + b"\\s"
    assert re.search(pattern, body)


def test_add_shell_from_buffer_fails(rest_api_client, mocked_responses):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    url = urljoin(API_URL, "Shells")
    err_msg = "Internal server error"
    mocked_responses.add(responses.POST, url, status=500, body=err_msg)
    expected_err = "Can't add shell, response: {err_msg}".format(**locals())

    with pytest.raises(PackagingRestApiError, match=expected_err):
        rest_api_client.add_shell_from_buffer(b"")


def test_add_shell(rest_api_client, mocked_responses, tmp_path):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    :type tmp_path: pathlib2.Path
    """
    url = urljoin(API_URL, "Shells")
    mocked_responses.add(responses.POST, url, status=201)

    file_content = b"test buffer"
    buffer = io.BytesIO(file_content)
    shell_name = "shell_name"
    file_name = "{shell_name}.zip".format(**locals())
    file_content = b"test buffer"
    shell_path = tmp_path / file_name
    shell_path.write_bytes(file_content)

    rest_api_client.add_shell(str(shell_path))

    assert len(mocked_responses.calls) == 2
    body = mocked_responses.calls[1].request.body
    pattern = b'filename=["\']' + file_name.encode() + b'["\']'
    assert re.search(pattern, body)
    pattern = b"\\s" + file_content + b"\\s"
    assert re.search(pattern, body)


def test_update_shell_from_buffer(rest_api_client, mocked_responses):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    shell_name = "shell_name"
    url = urljoin(API_URL, "Shells/{shell_name}".format(**locals()))
    mocked_responses.add(responses.PUT, url)

    file_content = b"test buffer"
    buffer = io.BytesIO(file_content)

    rest_api_client.update_shell_from_buffer(buffer, shell_name)

    assert len(mocked_responses.calls) == 2
    body = mocked_responses.calls[1].request.body
    assert re.search(b'filename=["\']file["\']', body)
    pattern = b"\\s" + file_content + b"\\s"
    assert re.search(pattern, body)


@pytest.mark.parametrize(
    ("status_code", "err_msg", "expected_err_class", "expected_err_text"),
    (
        (404, "", ShellNotFoundException, ""),
        (
            500,
            "Internal server error",
            PackagingRestApiError,
            "Can't update shell, response: Internal server error",
        ),
    ),
)
def test_update_shell_from_buffer_fails(
    status_code,
    err_msg,
    expected_err_class,
    expected_err_text,
    rest_api_client,
    mocked_responses,
):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    shell_name = "shell_name"
    url = urljoin(API_URL, "Shells/{shell_name}".format(**locals()))
    mocked_responses.add(responses.PUT, url, status=status_code, body=err_msg)

    with pytest.raises(expected_err_class, match=expected_err_text):
        rest_api_client.update_shell_from_buffer(b"", shell_name)


def test_update_shell(rest_api_client, mocked_responses, tmp_path):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    :type tmp_path: pathlib2.Path
    """
    shell_name = "shell_name"
    url = urljoin(API_URL, "Shells/{shell_name}".format(**locals()))
    mocked_responses.add(responses.PUT, url)

    file_content = b"test buffer"
    buffer = io.BytesIO(file_content)
    file_name = "{shell_name}.zip".format(**locals())
    file_content = b"test buffer"
    shell_path = tmp_path / file_name
    shell_path.write_bytes(file_content)

    rest_api_client.update_shell(str(shell_path))

    assert len(mocked_responses.calls) == 2
    body = mocked_responses.calls[1].request.body
    pattern = b'filename=["\']' + file_name.encode() + b'["\']'
    assert re.search(pattern, body)
    pattern = b"\\s" + file_content + b"\\s"
    assert re.search(pattern, body)


def test_get_shell(rest_api_client, mocked_responses):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    shell_name = "shell_name"
    url = urljoin(API_URL, "Shells/{shell_name}".format(**locals()))
    shell_info = {
        "Id": "5889f189-ecdd-404a-b6ff-b3d1e01a4cf3",
        "Name": shell_name,
        "Version": "2.0.1",
        "StandardType": "Networking",
        "ModificationDate": "2020-03-02T15:42:47",
        "LastModifiedByUser": {"Username": "admin", "Email": None},
        "Author": "Quali",
        "IsOfficial": True,
        "BasedOn": "",
        "ExecutionEnvironmentType": {"Position": 0, "Path": "2.7.10"},
    }
    mocked_responses.add(responses.GET, url, json=shell_info)

    assert rest_api_client.get_shell(shell_name) == shell_info


@pytest.mark.parametrize(
    ("status_code", "expected_err_class"),
    ((404, FeatureUnavailable), (400, ShellNotFoundException)),
)
def test_get_shell_fails(
    status_code, expected_err_class, rest_api_client, mocked_responses
):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    shell_name = "shell_name"
    url = urljoin(API_URL, "Shells/{shell_name}".format(**locals()))
    mocked_responses.add(responses.GET, url, status=status_code)

    with pytest.raises(expected_err_class):
        rest_api_client.get_shell(shell_name)


def test_delete_shell(rest_api_client, mocked_responses):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    shell_name = "shell_name"
    url = urljoin(API_URL, "Shells/{shell_name}".format(**locals()))
    mocked_responses.add(responses.DELETE, url)

    rest_api_client.delete_shell(shell_name)


@pytest.mark.parametrize(
    ("status_code", "err_msg", "expected_err_class", "expected_err_text"),
    (
        (404, "", FeatureUnavailable, ""),
        (400, "", ShellNotFoundException, ""),
        (500, "Internal server error", PackagingRestApiError, "Internal server error"),
    ),
)
def test_delete_shell_fails(
    status_code,
    err_msg,
    expected_err_class,
    expected_err_text,
    rest_api_client,
    mocked_responses,
):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    shell_name = "shell_name"
    url = urljoin(API_URL, "Shells/{shell_name}".format(**locals()))
    mocked_responses.add(responses.DELETE, url, status=status_code, body=err_msg)

    with pytest.raises(expected_err_class, match=expected_err_text):
        rest_api_client.delete_shell(shell_name)


def test_export_package(rest_api_client, mocked_responses):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    url = urljoin(API_URL, "Package/ExportPackage")
    byte_data = b"package_data"
    mocked_responses.add(responses.POST, url, byte_data)
    topologies = ["topology"]

    assert rest_api_client.export_package(topologies) == byte_data
    assert len(mocked_responses.calls) == 2
    body = mocked_responses.calls[1].request.body
    assert body == json.dumps({"TopologyNames": topologies})


@pytest.mark.parametrize(
    ("status_code", "err_msg", "expected_err_class", "expected_err_text"),
    (
        (404, "", FeatureUnavailable, ""),
        (500, "Internal server error", PackagingRestApiError, "Internal server error"),
    ),
)
def test_export_package(
    status_code,
    err_msg,
    expected_err_class,
    expected_err_text,
    rest_api_client,
    mocked_responses,
):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    url = urljoin(API_URL, "Package/ExportPackage")
    mocked_responses.add(responses.POST, url, status=status_code, body=err_msg)

    with pytest.raises(expected_err_class, match=expected_err_text):
        rest_api_client.export_package(["topology"])


def test_export_package_to_file(rest_api_client, mocked_responses, tmp_path):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    :type tmp_path: pathlib2.Path
    """
    url = urljoin(API_URL, "Package/ExportPackage")
    byte_data = b"package_data"
    mocked_responses.add(responses.POST, url, byte_data)
    topologies = ["topology"]
    file_path = tmp_path / "package.zip"

    rest_api_client.export_package_to_file(topologies, str(file_path))

    assert file_path.read_bytes() == byte_data
    assert len(mocked_responses.calls) == 2
    body = mocked_responses.calls[1].request.body
    assert body.decode() == json.dumps({"TopologyNames": topologies})


def test_import_package_from_buffer(rest_api_client, mocked_responses):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    url = urljoin(API_URL, "Package/ImportPackage")
    mocked_responses.add(responses.POST, url, json={"Success": True})
    file_content = b"test_buffer"
    buffer = io.BytesIO(file_content)

    rest_api_client.import_package_from_buffer(buffer)

    assert len(mocked_responses.calls) == 2
    body = mocked_responses.calls[1].request.body
    assert re.search(b'filename=["\']file["\']', body)
    pattern = b"\\s" + file_content + b"\\s"
    assert re.search(pattern, body)


@pytest.mark.parametrize(
    ("status_code", "err_msg", "expected_err_class", "expected_err_text"),
    (
        (404, "", FeatureUnavailable, ""),
        (500, "Internal server error", PackagingRestApiError, "Internal server error"),
    ),
)
def test_import_package_from_buffer_fails(
    status_code,
    err_msg,
    expected_err_class,
    expected_err_text,
    rest_api_client,
    mocked_responses,
):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    """
    url = urljoin(API_URL, "Package/ImportPackage")
    mocked_responses.add(responses.POST, url, status=status_code, body=err_msg)
    file_content = b"test_buffer"
    buffer = io.BytesIO(file_content)

    with pytest.raises(expected_err_class, match=expected_err_text):
        rest_api_client.import_package_from_buffer(buffer)


def test_import_package(rest_api_client, mocked_responses, tmp_path):
    """
    :type rest_api_client: PackagingRestApiClient
    :type mocked_responses: responses.RequestsMock
    :type tmp_path: pathlib2.Path
    """
    url = urljoin(API_URL, "Package/ImportPackage")
    mocked_responses.add(responses.POST, url, json={"Success": True})
    file_content = b"test_buffer"
    file_name = "package.zip"
    file_path = tmp_path / file_name
    file_path.write_bytes(file_content)

    rest_api_client.import_package(str(file_path))

    assert len(mocked_responses.calls) == 2
    body = mocked_responses.calls[1].request.body
    pattern = b'filename=["\']' + file_name.encode() + b'["\']'
    assert re.search(pattern, body)
    pattern = b"\\s" + file_content + b"\\s"
    assert re.search(pattern, body)
