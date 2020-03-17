import io
from pathlib import Path

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from cloudshell.rest.async_api import AsyncPackagingRestApiClient
from cloudshell.rest.exceptions import (
    FeatureUnavailable,
    PackagingRestApiError,
    ShellNotFoundException,
)
from pytests.conftest import PackagingApiTestServer, USERNAME, PASSWORD


@pytest.mark.asyncio
async def test_login(rest_api_client: AsyncPackagingRestApiClient):
    async def login(req: web.Request):
        received_data["text"] = await req.text()
        return web.Response(text=token)

    received_data = {}
    token = "token"
    app = web.Application()
    app.router.add_route("put", "/API/Auth/Login", login)

    async with TestServer(app, port=AsyncPackagingRestApiClient.DEFAULT_PORT):
        assert await rest_api_client._get_token() == token

    expected_text = f"username={USERNAME}&password={PASSWORD}&domain=Global"
    assert received_data["text"] == expected_text


@pytest.mark.asyncio
async def test_get_installed_standards(
    rest_api_client: AsyncPackagingRestApiClient, test_server: PackagingApiTestServer
):
    async def get_installed_standards(req: web.Request):
        return web.json_response(standards)

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
    test_server.app.router.add_route("get", "/API/Standards", get_installed_standards)
    async with test_server.start_server():
        assert await rest_api_client.get_installed_standards() == standards


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "text_msg", "expected_err_class", "expected_err_text"),
    (
        (404, "", FeatureUnavailable, ""),
        (500, "Internal server error", PackagingRestApiError, "Internal server error"),
    ),
)
async def test_get_installed_standards_failed(
    status_code,
    text_msg,
    expected_err_class,
    expected_err_text,
    rest_api_client: AsyncPackagingRestApiClient,
    test_server: PackagingApiTestServer,
):
    async def get_installed_standards(req: web.Request):
        return web.Response(text=text_msg, status=status_code)

    test_server.app.router.add_route("get", "/API/Standards", get_installed_standards)
    async with test_server.start_server():
        with pytest.raises(expected_err_class, match=expected_err_text):
            await rest_api_client.get_installed_standards()


@pytest.mark.asyncio
async def test_add_shell_from_buffer(
    rest_api_client: AsyncPackagingRestApiClient, test_server: PackagingApiTestServer
):
    async def add_shell(req: web.Request):
        received_data["post"] = await req.post()
        return web.Response(status=201)

    received_data = {}
    test_server.app.router.add_route("post", "/API/Shells", add_shell)
    file_content = b"test buffer"
    buffer = io.BytesIO(file_content)
    async with test_server.start_server():
        await rest_api_client.add_shell_from_buffer(buffer)

    assert len(received_data["post"]) == 1
    file_ = next(iter(received_data["post"].values()))
    assert file_.filename == "file"
    assert file_.file.read() == file_content


@pytest.mark.asyncio
async def test_add_shell_from_buffer_fails(
    rest_api_client: AsyncPackagingRestApiClient, test_server: PackagingApiTestServer
):
    async def add_shell(req: web.Request):
        return web.Response(status=500, text="Internal server error")

    test_server.app.router.add_route("post", "/API/Shells", add_shell)
    err_msg = "Internal server error"
    expected_err = f"Can't add shell, response: {err_msg}"
    async with test_server.start_server():
        with pytest.raises(PackagingRestApiError, match=expected_err):
            await rest_api_client.add_shell_from_buffer(b"")


@pytest.mark.asyncio
async def test_add_shell(
    rest_api_client: AsyncPackagingRestApiClient,
    test_server: PackagingApiTestServer,
    tmp_path: Path,
):
    async def add_shell(req: web.Request):
        received_data["post"] = await req.post()
        return web.Response(status=201)

    received_data = {}
    test_server.app.router.add_route("post", "/API/Shells", add_shell)
    shell_name = "shell_name"
    file_name = f"{shell_name}.zip"
    file_content = b"test buffer"
    shell_path = tmp_path / file_name
    shell_path.write_bytes(file_content)
    async with test_server.start_server():
        await rest_api_client.add_shell(shell_path)

    assert len(received_data["post"]) == 1
    file_ = next(iter(received_data["post"].values()))
    assert file_.filename == "file"
    assert file_.file.read() == file_content


@pytest.mark.asyncio
async def test_update_shell_from_buffer(
    rest_api_client: AsyncPackagingRestApiClient, test_server: PackagingApiTestServer
):
    async def update_shell(req: web.Request):
        received_data["name"] = req.match_info.get("name")
        received_data["post"] = await req.post()
        return web.Response()

    received_data = {}
    test_server.app.router.add_route("put", "/API/Shells/{name}", update_shell)
    shell_name = "shell_name"
    file_content = b"test buffer"
    buffer = io.BytesIO(file_content)
    async with test_server.start_server():
        await rest_api_client.update_shell_from_buffer(buffer, shell_name)

    assert received_data["name"] == shell_name
    assert len(received_data["post"]) == 1
    file_ = next(iter(received_data["post"].values()))
    assert file_.filename == "file"
    assert file_.file.read() == file_content


@pytest.mark.asyncio
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
async def test_update_shell_from_buffer_fails(
    status_code,
    err_msg,
    expected_err_class,
    expected_err_text,
    rest_api_client: AsyncPackagingRestApiClient,
    test_server: PackagingApiTestServer,
):
    async def update_shell(req: web.Request):
        return web.Response(status=status_code, text=err_msg)

    test_server.app.router.add_route("put", "/API/Shells/{name}", update_shell)
    shell_name = "shell_name"
    file_content = b"test buffer"
    buffer = io.BytesIO(file_content)
    async with test_server.start_server():
        with pytest.raises(expected_err_class, match=expected_err_text):
            await rest_api_client.update_shell_from_buffer(buffer, shell_name)


@pytest.mark.asyncio
async def test_update_shell(
    rest_api_client: AsyncPackagingRestApiClient,
    test_server: PackagingApiTestServer,
    tmp_path: Path,
):
    async def update_shell(req: web.Request):
        received_data["name"] = req.match_info.get("name")
        received_data["post"] = await req.post()
        return web.Response()

    received_data = {}
    test_server.app.router.add_route("put", "/API/Shells/{name}", update_shell)
    shell_name = "shell_name"
    file_name = f"{shell_name}.zip"
    file_content = b"test buffer"
    shell_path = tmp_path / file_name
    shell_path.write_bytes(file_content)
    async with test_server.start_server():
        await rest_api_client.update_shell(shell_path)

    assert received_data["name"] == shell_name
    assert len(received_data["post"]) == 1
    file_ = next(iter(received_data["post"].values()))
    assert file_.filename == "file"
    assert file_.file.read() == file_content


@pytest.mark.asyncio
async def test_get_shell(
    rest_api_client: AsyncPackagingRestApiClient, test_server: PackagingApiTestServer
):
    async def get_shell(req: web.Request):
        received_data["name"] = req.match_info.get("name")
        return web.json_response(shell_info)

    received_data = {}
    test_server.app.router.add_route("get", "/API/Shells/{name}", get_shell)
    shell_name = "shell_name"
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
    async with test_server.start_server():
        assert await rest_api_client.get_shell(shell_name) == shell_info

    assert received_data["name"] == shell_name


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "expected_err_class"),
    ((404, FeatureUnavailable), (400, ShellNotFoundException)),
)
async def test_get_shell_fails(
    status_code,
    expected_err_class,
    rest_api_client: AsyncPackagingRestApiClient,
    test_server: PackagingApiTestServer,
):
    async def get_shell(req: web.Request):
        return web.Response(status=status_code)

    test_server.app.router.add_route("get", "/API/Shells/{name}", get_shell)
    async with test_server.start_server():
        with pytest.raises(expected_err_class):
            await rest_api_client.get_shell("shell_name")


@pytest.mark.asyncio
async def test_delete_shell(
    rest_api_client: AsyncPackagingRestApiClient, test_server: PackagingApiTestServer
):
    async def delete_shell(req: web.Request):
        received_data["name"] = req.match_info.get("name")
        return web.Response()

    received_data = {}
    test_server.app.router.add_route("delete", "/API/Shells/{name}", delete_shell)
    shell_name = "shell_name"
    async with test_server.start_server():
        await rest_api_client.delete_shell(shell_name)

    assert received_data["name"] == shell_name


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "err_msg", "expected_err_class", "expected_err_text"),
    (
        (404, "", FeatureUnavailable, ""),
        (400, "", ShellNotFoundException, ""),
        (500, "Internal server error", PackagingRestApiError, "Internal server error"),
    ),
)
async def test_delete_shell_fails(
    status_code,
    err_msg,
    expected_err_class,
    expected_err_text,
    rest_api_client: AsyncPackagingRestApiClient,
    test_server: PackagingApiTestServer,
):
    async def delete_shell(req: web.Request):
        return web.Response(status=status_code, text=err_msg)

    test_server.app.router.add_route("delete", "/API/Shells/{name}", delete_shell)
    async with test_server.start_server():
        with pytest.raises(expected_err_class, match=expected_err_text):
            await rest_api_client.delete_shell("shell_name")


@pytest.mark.asyncio
async def test_export_package(
    rest_api_client: AsyncPackagingRestApiClient, test_server: PackagingApiTestServer
):
    async def export_package(req: web.Request):
        received_data["json"] = await req.json()
        return web.Response(body=byte_data)

    received_data = {}
    byte_data = b"package_data"
    topologies = ["topology"]
    test_server.app.router.add_route(
        "post", "/API/Package/ExportPackage", export_package
    )
    async with test_server.start_server():
        assert await rest_api_client.export_package(topologies) == byte_data

    assert received_data["json"] == {"TopologyNames": topologies}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "err_msg", "expected_err_class", "expected_err_text"),
    (
        (404, "", FeatureUnavailable, ""),
        (500, "Internal server error", PackagingRestApiError, "Internal server error"),
    ),
)
async def test_export_package_fails(
    status_code,
    err_msg,
    expected_err_class,
    expected_err_text,
    rest_api_client: AsyncPackagingRestApiClient,
    test_server: PackagingApiTestServer,
):
    async def export_package(req: web.Request):
        return web.Response(status=status_code, text=err_msg)

    test_server.app.router.add_route(
        "post", "/API/Package/ExportPackage", export_package
    )
    async with test_server.start_server():
        with pytest.raises(expected_err_class, match=expected_err_text):
            await rest_api_client.export_package(["topology"])


@pytest.mark.asyncio
async def test_export_package_to_file(
    rest_api_client: AsyncPackagingRestApiClient,
    test_server: PackagingApiTestServer,
    tmp_path: Path,
):
    async def export_package(req: web.Request):
        return web.Response(body=byte_data)

    byte_data = b"package_data"
    topologies = ["topology"]
    file_path = tmp_path / "package.zip"
    test_server.app.router.add_route(
        "post", "/API/Package/ExportPackage", export_package
    )
    async with test_server.start_server():
        await rest_api_client.export_package_to_file(topologies, file_path)

    assert file_path.read_bytes() == byte_data


@pytest.mark.asyncio
async def test_import_package_from_buffer(
    rest_api_client: AsyncPackagingRestApiClient, test_server: PackagingApiTestServer
):
    async def import_package(req: web.Request):
        received_data["post"] = await req.post()
        return web.json_response({"Success": True})

    received_data = {}
    file_content = b"test buffer"
    buffer = io.BytesIO(file_content)
    test_server.app.router.add_route(
        "post", "/API/Package/ImportPackage", import_package
    )
    async with test_server.start_server():
        await rest_api_client.import_package_from_buffer(buffer)

    assert len(received_data["post"]) == 1
    file_ = next(iter(received_data["post"].values()))
    assert file_.filename == "file"
    assert file_.file.read() == file_content


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "err_msg", "expected_err_class", "expected_err_text"),
    (
        (404, "", FeatureUnavailable, ""),
        (500, "Internal server error", PackagingRestApiError, "Internal server error"),
    ),
)
async def test_import_package_from_buffer_fails(
    status_code,
    err_msg,
    expected_err_class,
    expected_err_text,
    rest_api_client: AsyncPackagingRestApiClient,
    test_server: PackagingApiTestServer,
):
    async def import_package(req: web.Request):
        return web.Response(status=status_code, text=err_msg)

    file_content = b"test buffer"
    buffer = io.BytesIO(file_content)
    test_server.app.router.add_route(
        "post", "/API/Package/ImportPackage", import_package
    )
    async with test_server.start_server():
        with pytest.raises(expected_err_class, match=expected_err_text):
            await rest_api_client.import_package_from_buffer(buffer)


@pytest.mark.asyncio
async def test_import_package(
    rest_api_client: AsyncPackagingRestApiClient,
    test_server: PackagingApiTestServer,
    tmp_path: Path,
):
    async def import_package(req: web.Request):
        received_data["post"] = await req.post()
        return web.json_response({"Success": True})

    received_data = {}
    file_content = b"test buffer"
    file_name = "package.zip"
    file_path = tmp_path / file_name
    file_path.write_bytes(file_content)
    test_server.app.router.add_route(
        "post", "/API/Package/ImportPackage", import_package
    )
    async with test_server.start_server():
        await rest_api_client.import_package(file_path)

    assert len(received_data["post"]) == 1
    file_ = next(iter(received_data["post"].values()))
    assert file_.filename == "file"
    assert file_.file.read() == file_content
