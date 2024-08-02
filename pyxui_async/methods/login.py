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
