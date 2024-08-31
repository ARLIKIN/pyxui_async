import json
from typing import Union

import aiohttp

import pyxui_async
from pyxui_async import errors


class Base:
    async def request(
            self: "pyxui_async.XUI",
            path: str,
            method: str,
            params: dict = None
    ) -> Union[dict, errors.NotFound]:
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

        self.session = aiohttp.ClientSession(cookies=cookie)

        if method == "GET":
            response = await self.session.get(url, ssl=self.https)
        elif method == "POST":
            response = await self.session.post(
                    url,
                    data=params,
                    ssl=self.https
            )
        else:
            raise errors.NotFound()

        if path == "login":
            self.session_string = response.cookies.get(self.cookie_name)
            if self.session_string is None:
                self.session_string = response.cookies.get(self.old_cookie_name)
                self.cookie_name = self.old_cookie_name

        return await self.verify_response(response)

    async def verify_response(
            self: "pyxui_async.XUI",
            response: aiohttp.ClientResponse
    ):
        content_type = response.headers.get('Content-Type', '')
        if response.status != 404 and content_type.startswith(
                'application/json'):
            response = await response.json()
            await self.session.close()
            return response

        raise errors.NotFound()
