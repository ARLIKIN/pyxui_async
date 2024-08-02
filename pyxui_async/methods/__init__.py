from pyxui_async.methods.base import Base
from pyxui_async.methods.login import Login
from pyxui_async.methods.inbounds import Inbounds
from pyxui_async.methods.clients import Clients

class Methods(
    Base,
    Login,
    Inbounds,
    Clients
):
    pass
