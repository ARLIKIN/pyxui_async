from pyxui_async.methods.base import Base
from pyxui_async.methods.custom import Custom
from pyxui_async.methods.clients import Client
from pyxui_async.methods.inbounds import Inbounds
from pyxui_async.methods.login import Login
from pyxui_async.methods.servers import Server


class Methods(
    Base,
    Inbounds,
    Client,
    Custom,
    Login,
    Server
):
    pass