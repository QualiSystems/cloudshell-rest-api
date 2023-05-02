import io
import json
import re
from urllib.parse import parse_qs, urljoin

import pytest
import responses

from cloudshell.rest.api import PackagingRestApiClient
from cloudshell.rest.exceptions import (
    FeatureUnavailable,
    LoginFailedError,
    PackagingRestApiError,
    ShellNotFound,
)

HOST = "host"
PORT = 9000
USERNAME = "username"
PASSWORD = "password"
DOMAIN = "Global"
TOKEN = "token"
API_URL = f"http://{HOST}:{PORT}/API/"


@pytest.fixture
def rest_api_client():
    return PackagingRestApiClient(HOST, TOKEN)


def test_login():
    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, urljoin(API_URL, "Auth/Login"), body=TOKEN)

        api = PackagingRestApiClient.login(
            HOST, USERNAME, PASSWORD, domain=DOMAIN, port=PORT
        )
        assert api._token == TOKEN

        assert len(rsps.calls) == 1
        req = rsps.calls[0].request

    body = "username={USERNAME}&domain={DOMAIN}&password={PASSWORD}".format(**globals())
    assert parse_qs(req.body) == parse_qs(body)


@pytest.mark.parametrize(
    ("status_code", "err_msg", "expected_err_class", "expected_err_text"),
    (
        (401, "", LoginFailedError, ""),
        (500, "Internal server error", PackagingRestApiError, "Internal server error"),
    ),
)
def test_login_failed(status_code, err_msg, expected_err_class, expected_err_text):
    url = urljoin(API_URL, "Auth/Login")
    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, url, body=err_msg, status=status_code)

        with pytest.raises(expected_err_class, match=expected_err_text):
            PackagingRestApiClient.login(HOST, USERNAME, PASSWORD)


def test_get_installed_standards(rest_api_client):
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

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, json=standards)

        assert rest_api_client.get_installed_standards() == standards


def test_get_installed_standards_as_models(rest_api_client):
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

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, json=standards)

        models = rest_api_client.get_installed_standards_as_models()

    for i in range(2):
        assert models[i].standard_name == standards[i]["StandardName"]
        assert models[i].versions == standards[i]["Versions"]
    m = models[0]
    expected_repr = (
        "StandardInfo(standard_name='cloudshell_firewall_standard', "
        "versions=['3.0.0', '3.0.1', '3.0.2'])"
    )
    assert str(m) == expected_repr


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
):
    url = urljoin(API_URL, "Standards")

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=status_code, body=text_msg)

        with pytest.raises(expected_err_class, match=expected_err_text):
            rest_api_client.get_installed_standards()


def test_add_shell_from_buffer(rest_api_client):
    url = urljoin(API_URL, "Shells")
    file_content = b"test buffer"
    buffer = io.BytesIO(file_content)

    with responses.RequestsMock() as rsps:
        rsps.add(responses.POST, url, status=201)

        rest_api_client.add_shell_from_buffer(buffer)

        assert len(rsps.calls) == 1
        body = rsps.calls[0].request.body

    assert re.search(b"filename=[\"']file[\"']", body)
    pattern = b"\\s" + file_content + b"\\s"
    assert re.search(pattern, body)


def test_add_shell_from_buffer_fails(rest_api_client):
    url = urljoin(API_URL, "Shells")
    err_msg = "Internal server error"
    expected_err = f"Can't add shell, response: {err_msg}"

    with responses.RequestsMock() as rsps:
        rsps.add(responses.POST, url, status=500, body=err_msg)

        with pytest.raises(PackagingRestApiError, match=expected_err):
            rest_api_client.add_shell_from_buffer(b"")


def test_add_shell(rest_api_client, tmp_path):
    url = urljoin(API_URL, "Shells")

    file_content = b"test buffer"
    _ = io.BytesIO(file_content)
    shell_name = "shell_name"
    file_name = f"{shell_name}.zip"
    file_content = b"test buffer"
    shell_path = tmp_path / file_name
    shell_path.write_bytes(file_content)

    with responses.RequestsMock() as rsps:
        rsps.add(responses.POST, url, status=201)

        rest_api_client.add_shell(str(shell_path))

        assert len(rsps.calls) == 1
        body = rsps.calls[0].request.body

    pattern = b"filename=[\"']" + file_name.encode() + b"[\"']"
    assert re.search(pattern, body)
    pattern = b"\\s" + file_content + b"\\s"
    assert re.search(pattern, body)


def test_update_shell_from_buffer(rest_api_client):
    shell_name = "shell_name"
    url = urljoin(API_URL, f"Shells/{shell_name}")

    file_content = b"test buffer"
    buffer = io.BytesIO(file_content)

    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, url)

        rest_api_client.update_shell_from_buffer(buffer, shell_name)

        assert len(rsps.calls) == 1
        body = rsps.calls[0].request.body

    assert re.search(b"filename=[\"']file[\"']", body)
    pattern = b"\\s" + file_content + b"\\s"
    assert re.search(pattern, body)


@pytest.mark.parametrize(
    ("status_code", "err_msg", "expected_err_class", "expected_err_text"),
    (
        (404, "", ShellNotFound, ""),
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
):
    shell_name = "shell_name"
    url = urljoin(API_URL, f"Shells/{shell_name}")

    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, url, status=status_code, body=err_msg)

        with pytest.raises(expected_err_class, match=expected_err_text):
            rest_api_client.update_shell_from_buffer(b"", shell_name)


def test_update_shell(rest_api_client, tmp_path):
    shell_name = "shell_name"
    url = urljoin(API_URL, f"Shells/{shell_name}")

    file_content = b"test buffer"
    _ = io.BytesIO(file_content)
    file_name = f"{shell_name}.zip"
    file_content = b"test buffer"
    shell_path = tmp_path / file_name
    shell_path.write_bytes(file_content)

    with responses.RequestsMock() as rsps:
        rsps.add(responses.PUT, url)

        rest_api_client.update_shell(str(shell_path))

        assert len(rsps.calls) == 1
        body = rsps.calls[0].request.body

    pattern = b"filename=[\"']" + file_name.encode() + b"[\"']"
    assert re.search(pattern, body)
    pattern = b"\\s" + file_content + b"\\s"
    assert re.search(pattern, body)


def test_get_shell(rest_api_client):
    shell_name = "shell_name"
    url = urljoin(API_URL, f"Shells/{shell_name}")
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

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, json=shell_info)

        assert rest_api_client.get_shell(shell_name) == shell_info


def test_get_shell_as_model(rest_api_client):
    shell_name = "shell_name"
    url = urljoin(API_URL, f"Shells/{shell_name}")
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
    expected_user_repr = "UserInfo(user_name='admin', email=None)"
    expected_exec_env_repr = "ExecutionEnvironmentType(position=0, path='2.7.10')"
    expected_shell_repr = (
        "ShellInfo(name='shell_name', version='2.0.1', is_official=True)"
    )

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, json=shell_info)

        model = rest_api_client.get_shell_as_model(shell_name)

    assert model.id == shell_info["Id"]
    assert model.name == shell_info["Name"]
    assert model.version == shell_info["Version"]
    assert model.standard_type == shell_info["StandardType"]
    assert model.modification_date == shell_info["ModificationDate"]
    assert (
        model.last_modified_by_user.user_name
        == shell_info["LastModifiedByUser"]["Username"]
    )
    assert (
        model.last_modified_by_user.email == shell_info["LastModifiedByUser"]["Email"]
    )
    assert model.author == shell_info["Author"]
    assert model.is_official == shell_info["IsOfficial"]
    assert model.based_on == shell_info["BasedOn"]
    assert (
        model.execution_environment_type.position
        == shell_info["ExecutionEnvironmentType"]["Position"]
    )
    assert (
        model.execution_environment_type.path
        == shell_info["ExecutionEnvironmentType"]["Path"]
    )
    assert str(model) == expected_shell_repr
    assert str(model.last_modified_by_user) == expected_user_repr
    assert str(model.execution_environment_type) == expected_exec_env_repr


@pytest.mark.parametrize(
    ("status_code", "err_msg", "expected_err_class", "expected_err_text"),
    (
        (404, "", FeatureUnavailable, ""),
        (400, "", ShellNotFound, ""),
        (500, "Internal server error", PackagingRestApiError, "Internal server error"),
    ),
)
def test_get_shell_fails(
    status_code,
    err_msg,
    expected_err_class,
    expected_err_text,
    rest_api_client,
):
    shell_name = "shell_name"
    url = urljoin(API_URL, f"Shells/{shell_name}")

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=status_code)

        with pytest.raises(expected_err_class):
            rest_api_client.get_shell(shell_name)


def test_delete_shell(rest_api_client):
    shell_name = "shell_name"
    url = urljoin(API_URL, f"Shells/{shell_name}")

    with responses.RequestsMock() as rsps:
        rsps.add(responses.DELETE, url)

        rest_api_client.delete_shell(shell_name)


@pytest.mark.parametrize(
    ("status_code", "err_msg", "expected_err_class", "expected_err_text"),
    (
        (404, "", FeatureUnavailable, ""),
        (400, "", ShellNotFound, ""),
        (500, "Internal server error", PackagingRestApiError, "Internal server error"),
    ),
)
def test_delete_shell_fails(
    status_code,
    err_msg,
    expected_err_class,
    expected_err_text,
    rest_api_client,
):
    shell_name = "shell_name"
    url = urljoin(API_URL, f"Shells/{shell_name}")

    with responses.RequestsMock() as rsps:
        rsps.add(responses.DELETE, url, status=status_code, body=err_msg)

        with pytest.raises(expected_err_class, match=expected_err_text):
            rest_api_client.delete_shell(shell_name)


def test_export_package(rest_api_client):
    url = urljoin(API_URL, "Package/ExportPackage")
    byte_data = b"package_data"
    topologies = ["topology"]

    with responses.RequestsMock() as rsps:
        rsps.add(responses.POST, url, byte_data)

        assert rest_api_client.export_package(topologies) == byte_data

        assert len(rsps.calls) == 1
        body = rsps.calls[0].request.body

    assert body == json.dumps({"TopologyNames": topologies}).encode()


@pytest.mark.parametrize(
    ("status_code", "err_msg", "expected_err_class", "expected_err_text"),
    (
        (404, "", FeatureUnavailable, ""),
        (500, "Internal server error", PackagingRestApiError, "Internal server error"),
    ),
)
def test_export_package_fails(
    status_code,
    err_msg,
    expected_err_class,
    expected_err_text,
    rest_api_client,
):
    url = urljoin(API_URL, "Package/ExportPackage")

    with responses.RequestsMock() as rsps:
        rsps.add(responses.POST, url, status=status_code, body=err_msg)

        with pytest.raises(expected_err_class, match=expected_err_text):
            rest_api_client.export_package(["topology"])


def test_export_package_to_file(rest_api_client, tmp_path):
    url = urljoin(API_URL, "Package/ExportPackage")
    byte_data = b"package_data"
    topologies = ["topology"]
    file_path = tmp_path / "package.zip"

    with responses.RequestsMock() as rsps:
        rsps.add(responses.POST, url, byte_data)

        rest_api_client.export_package_to_file(topologies, str(file_path))

        assert file_path.read_bytes() == byte_data
        assert len(rsps.calls) == 1
        body = rsps.calls[0].request.body

    assert body.decode() == json.dumps({"TopologyNames": topologies})


def test_import_package_from_buffer(rest_api_client):
    url = urljoin(API_URL, "Package/ImportPackage")
    file_content = b"test_buffer"
    buffer = io.BytesIO(file_content)

    with responses.RequestsMock() as rsps:
        rsps.add(responses.POST, url, json={"Success": True})

        rest_api_client.import_package_from_buffer(buffer)

        assert len(rsps.calls) == 1
        body = rsps.calls[0].request.body

    assert re.search(b"filename=[\"']file[\"']", body)
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
):
    url = urljoin(API_URL, "Package/ImportPackage")
    file_content = b"test_buffer"
    buffer = io.BytesIO(file_content)

    with responses.RequestsMock() as rsps:
        rsps.add(responses.POST, url, status=status_code, body=err_msg)

        with pytest.raises(expected_err_class, match=expected_err_text):
            rest_api_client.import_package_from_buffer(buffer)


def test_import_package(rest_api_client, tmp_path):
    url = urljoin(API_URL, "Package/ImportPackage")
    file_content = b"test_buffer"
    file_name = "package.zip"
    file_path = tmp_path / file_name
    file_path.write_bytes(file_content)

    with responses.RequestsMock() as rsps:
        rsps.add(responses.POST, url, json={"Success": True})

        rest_api_client.import_package(str(file_path))

        assert len(rsps.calls) == 1
        body = rsps.calls[0].request.body

    pattern = b"filename=[\"']" + file_name.encode() + b"[\"']"
    assert re.search(pattern, body)
    pattern = b"\\s" + file_content + b"\\s"
    assert re.search(pattern, body)
