import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from cloudshell.rest.async_api import AsyncPackagingRestApiClient

HOST = "localhost"
USERNAME = "test_user"
PASSWORD = "test_password"


class PackagingApiTestServer:
    def __init__(self, app: web.Application):
        self.app = app
        self.port = AsyncPackagingRestApiClient.DEFAULT_PORT

    def start_server(self):
        return TestServer(self.app, port=self.port)


@pytest.fixture()
def rest_api_client():
    return AsyncPackagingRestApiClient(HOST, USERNAME, PASSWORD)


@pytest.fixture()
def packaging_app_with_token():
    async def login(req: web.Request):
        return web.Response(text=token)

    token = "token"
    app = web.Application()
    app.router.add_route("put", "/API/Auth/Login", login)
    return app


@pytest.fixture()
def test_server(packaging_app_with_token: web.Application):
    return PackagingApiTestServer(packaging_app_with_token)
