import aiohttp

import pyxui_async
from pyxui_async import errors


class Base:
    async def request(
            self: "pyxui_async.XUI",
            path: str,
            method: str,
            params: dict = None
    ) -> aiohttp.ClientResponse:
        """Request to the xui panel.

        Parameters:
            path (``str``):
                The request path, you can see all of them in https://github.com/alireza0/x-ui#api-routes

            method (``str``):
                The request method, GET or POST

            params (``dict``, optional):
                The request parameters, None is set for default but it's necessary for some POST methods

        Returns:
            `~aiohttp.ClientResponse`: On success, the response is returned.
        """

        if path == "login":
            url = f"{self.full_address}/login"
        else:
            url = f"{self.full_address}/{self.api_path}/inbounds/{path}"

        if self.session_string:
            cookie = {self.cookie_name: self.session_string}
        else:
            cookie = None

        async with aiohttp.ClientSession(cookies=cookie) as session:
            if method == "GET":
                async with session.get(url, ssl=self.https) as response:
                    return await response.text()
            elif method == "POST":
                async with session.post(url, data=params,
                                        ssl=self.https) as response:
                    return await response.text()

    async def verify_response(
            self: "pyxui_async.XUI",
            response: aiohttp.ClientResponse
    ) -> dict:
        content_type = response.headers.get('Content-Type', '')
        if response.status != 404 and content_type.startswith(
                'application/json'):
            return await response.json()

        raise errors.NotFound()
