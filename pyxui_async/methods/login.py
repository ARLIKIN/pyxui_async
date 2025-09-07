import json
from typing import Any

import pyxui_async
from pyxui_async import errors


class Login:
    async def login(
        self: "pyxui_async.XUI",
        username: str,
        password: str
    ) -> Any:
        """Login into xui panel.

        Parameters:
            username (``str``):
                Username of panel

            password (``str``):
                Password of panel

        Returns:
            `~Any`: On success, True is returned else an error will be raised
        """
        if self.session_string:
            raise errors.AlreadyLogin()
        try:
            send_request = await self.request(
                path="login",
                method="POST",
                params={
                    'username': username,
                    'password': password
                }
            )

            if send_request['success'] and self.session_string:
                return True

            raise errors.BadLogin()

        except Exception as e:
            await self._close_session()
            raise

    async def _close_session(self):
        if hasattr(
            self,'session'
        ) and self.session and not self.session.closed:
            await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_session()
