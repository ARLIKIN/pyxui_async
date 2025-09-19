# PyXUI Async
An application with python that allows you to modify your xui panel ([Sanaeii 3x-ui](https://github.com/MHSanaei/3x-ui)) 

## How To Install
```
pip install pyxui_async
```

## How To Use
- Import pyxui in your .py file

```python
from pyxui_async import XUI

xui = XUI(
    full_address="http://staliox.site:2087",
    panel="sanaei",  # Your panel name "sanaei"
    https=False,  # Make note if you don't use https set False else set True
    timeout=30 # timeout connect
)
```

- Login in your panel

```python
from pyxui_async.errors import BadLogin

try:
   await xui.login(USERNAME, PASSWORD)
except BadLogin:
    ...
```

- Get inbounds list
```python
get_inbounds = await xui.get_inbounds()

# Result is object InboundsResponse
class InboundsResponse(ResponseBase):
    success: bool
    msg: str
    obj: List[
        id: int
        up: int
        down: int
        total: int
        allTime: Optional[int] = None
        remark: str
        enable: bool
        expiryTime: int
        clientStats: Optional[List[InboundClientStats]] = []
        listen: str
        port: int
        protocol: str
        settings: InboundSettings
        streamSettings: Optional[StreamSettings] = None
        tag: str
        sniffing: Sniffing
    ]
```

- Add client to the existing inbound
```python
new_id = await xui.get_new_uuid()
get = await xui.add_clients(
    inbound_id=1,
    client_settings=ClientSettings(clients=[Client(
        id=new_id.obj.uuid,
        email="example@gmal.com",
        flow = "xtls-rprx-vision",
        subscription_id = "Asaw3ras3asdfa1was"
    )])
)
```
If you add trojan or ShadowSoks, you must specify a password for the id.

- Update the existing client
```python
get = await xui.update_client(
    inbound_id=1,
    email="example@gmal.com",
    uuid="5d3d1bac-49cd-4b66-8be9-a728efa205fa",
    enable = True,
    flow = "",
    limit_ip = 0,
    total_gb = 5368709120,
    expire_time = 1684948641772,
    telegram_id = "",
    subscription_id = ""
)
```

- Get client's information:
```python
get_client = await xui.get_client(
    inbound_id=1,
    email="Me",
)

# Result
class Client(BaseModel):
    id: Optional[str] = ""
    flow: Optional[str] = ""
    email: str
    limitIp: Optional[int] = 0
    totalGB: Optional[int] = 0
    expiryTime: Optional[int] = 0
    enable: Optional[bool] = True
    tgId: Optional[Any] = ""
    subId: Optional[str] = ""
    reset: Optional[int] = 0
    comment: Optional[str] = ""
    security: Optional[str] = ""
    password: Optional[str] = ""
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
```

- Get client's statistics:
```python
get_client = await xui.get_client_stat(
    inbound_id=1,
    email="Me",
)

# Result
class InboundClientStats(BaseModel):
    id: int
    inboundId: int
    enable: bool
    email: str
    up: int
    down: int
    allTime: Optional[int] = None
    expiryTime: int
    total: int
    reset: int
    lastOnline: Optional[int] = None
```

- Delete client from the existing inbound:
```python
get_client = await xui.delete_client(
    inbound_id=1,
    email="Me",
    uuid="5d3d1bac-49cd-4b66-8be9-a728efa205fa" # Make note you don't have to pass both of them (email, uuid), just one is enough
)
```

# Create config string
```python
    key_vless = await xui.get_key_vless(inbound_id=1, email='email', custom_remark='Mary')
    key_trojan = await xui.get_key_trojan(inbound_id=2, email='email', custom_remark='Elsa')
    key_shadow_soks = await xui.get_key_shadow_socks(inbound_id=3, email='email', custom_remark='Dani')
    sub_url = await xui.get_subscription_link(
        inbound_id=4, email='email', https=True, port=443, sub_path='/myserver/'
    )
```
