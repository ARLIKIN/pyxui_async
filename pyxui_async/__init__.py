from pyxui_async.methods import Methods
from pyxui_async.models import *


class XUI(Methods):
    def __init__(
        self,
        full_address: str,
        panel: str = "",
        https: bool = False,
        timeout: int = 30,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        super().__init__(
            full_address, panel, https, timeout, username, password
        )
