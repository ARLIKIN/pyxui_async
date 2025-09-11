from typing import Optional, Union

from pyxui_async.errors import BadLogin, AlreadyLogin
from pyxui_async.models import ResponseBase, POST


class Login:
    async def login(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> Union[ResponseBase, BadLogin, AlreadyLogin]:
        """
        Авторизация пользователя в панели XUI.
        Генерирует исключение BadLogin, если логин или пароль неверны.
        Генерирует исключение AlreadyLogin, если пользователь уже авторизован.
        """
        if self._session is not None:
            raise AlreadyLogin()
        data = {
            'username': username or self.username,
            'password': password or self.password
        }
        result = await self.request(
            method=POST, endpoint='/login/', data=data
        )
        if result.get('success', False):
            return ResponseBase(**result)
        raise BadLogin()
