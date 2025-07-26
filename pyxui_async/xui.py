from aiohttp import ClientTimeout

from pyxui_async.methods import Methods

class XUI(Methods):
    def __init__(
        self,
        full_address: str,
        panel: str,
        https: bool = True,
        session_string: str = None,
        timeout: float = 30
    ) -> None:
        super().__init__()

        self.full_address = full_address
        self.panel = panel
        self.https = https
        self.session_string = session_string
        self.timeout = ClientTimeout(total=timeout)

        if self.panel == "alireza":
            self.api_path = "xui/API"
            self.cookie_name = "x-ui"
            
        elif self.panel == "sanaei":
            self.api_path = "panel/api"
            self.cookie_name = "3x-ui"
            self.old_cookie_name = 'session'