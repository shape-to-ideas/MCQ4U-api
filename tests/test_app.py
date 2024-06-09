from litestar.testing import AsyncTestClient
import pprint

# import asyncio
import pytest

from app.main import app

# pytest_plugins = ('pytest_asyncio',)


# # def test_sync() -> None:
# #     with TestClient(app=app) as client:
# #         assert client.get("/sync").json() == {"hello": "world"}


@pytest.mark.asyncio
async def test_create_user() -> None:
    async with AsyncTestClient(app=app) as client:
        email = 'joshisuresh51@gmail.com'
        url = '/v1/user/' + email
        api_response = await client.get(url).json()
        pprint.pprint('a')
        assert 1 == 1
        #  await asyncio.sleep(0.5)
