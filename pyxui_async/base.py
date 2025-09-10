import logging

import aiohttp
from typing import Optional, Dict, Any, Union

from aiohttp import ClientConnectorError

from pyxui_async.errors import NotFound


class Base:
    def __init__(
        self,
        full_address: str,
        panel: str = "",
        https: bool = False,
        timeout: int = 30,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.address = full_address.rstrip("/")
        self.panel = panel
        self.https = https
        self.timeout = timeout
        self.cookies: Dict[str, str] = {}
        self.username = username
        self.password = password
        self._session: Optional[aiohttp.ClientSession] = None
        self._closed = True

    async def open(self):
        if self._session is None or self._closed:
            self._session = aiohttp.ClientSession()
            self._closed = False

    async def close(self):
        if self._session and not self._closed:
            await self._session.close()
            self._closed = True

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        json: Any = None,
        data: Any = None,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
    ) -> Union[dict, NotFound]:
        await self.open()
        url = f"{self.address}{endpoint}"
        headers = headers or {}
        if self.cookies:
            headers['Cookie'] = "; ".join(f"{k}={v}" for k, v in self.cookies.items())
        try:
            async with self._session.request(
                method,
                url,
                json=json,
                data=data,
                params=params,
                headers=headers,
                timeout=self.timeout,
                ssl=self.https
            ) as response:
                for cookie in response.cookies.values():
                    self.cookies[cookie.key] = cookie.value
                return await verify_response(response)
        except Exception as e:
            logging.error(e)
            raise
        finally:
            await self.close()

async def verify_response(
        response: aiohttp.ClientResponse
) -> Union[dict, NotFound]:
    content_type = response.headers.get('Content-Type', '')
    if response.status != 404 and content_type.startswith(
            'application/json'):
        response = await response.json()
        return response
    raise NotFound()