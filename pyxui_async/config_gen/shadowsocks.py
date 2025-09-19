import urllib.parse
import base64
from typing import Optional, Union

from pyxui_async.errors import NotFound
from pyxui_async.models import Inbound


async def build_shadowsocks_from_inbound(
        inbound: Inbound,
        email: str,
        address: str,
        custom_remark: Optional[str] = None,
) -> Union[str, ValueError, NotFound]:
    """
    Собирает из данных подключения ключ пользователя ShadowSocks.
    """
    if inbound.protocol.lower() != 'shadowsocks':
        raise ValueError(
            f"The protocol must be ShadowSocks, received: {inbound.protocol}"
        )
    if not inbound.settings.clients or len(inbound.settings.clients) == 0:
        raise ValueError("There are no clients in Inbound")
    client = None
    for client_setting in inbound.settings.clients:
        if client_setting.email != email:
            continue
        client = client_setting
    if client is None:
        raise NotFound()
    method = '2022-blake3-aes-256-gcm'
    if hasattr(inbound.settings, 'method') and inbound.settings.method:
        method = inbound.settings.method
    elif hasattr(inbound, 'method') and inbound.method:
        method = inbound.method
    server_password = ''
    if hasattr(inbound.settings, 'password') and inbound.settings.password:
        server_password = inbound.settings.password
    elif hasattr(inbound, 'password') and inbound.password:
        server_password = inbound.password

    elif inbound.settings.clients and len(inbound.settings.clients) > 0:
        first_client = inbound.settings.clients[0]
        if hasattr(first_client, 'password') and first_client.password:
            server_password = first_client.password
    if method in ['aes-256-gcm', 'chacha20-poly1305', 'chacha20-ietf-poly1305', 'xchacha20-ietf-poly1305']:
        auth_string = f"{method}:{client.password}"
    else:
        auth_string = f"{method}:{server_password}:{client.password}"
    user_base64 = base64.b64encode(auth_string.encode()).decode().rstrip('=')
    params = {}
    if inbound.streamSettings:
        stream = inbound.streamSettings
        params["type"] = stream.network if stream.network else "tcp"
        if stream.security and stream.security != "none":
            params["security"] = stream.security
            if stream.security == "tls" and stream.tlsSettings:
                if hasattr(stream.tlsSettings,
                           'settings') and stream.tlsSettings.settings:
                    if hasattr(stream.tlsSettings.settings, 'fingerprint'):
                        params["fp"] = stream.tlsSettings.settings.fingerprint
                    if hasattr(stream.tlsSettings,
                               'alpn') and stream.tlsSettings.alpn:
                        params["alpn"] = ','.join(stream.tlsSettings.alpn)
                    if hasattr(stream.tlsSettings.settings, 'echConfigList'):
                        params["ech"] = stream.tlsSettings.settings.echConfigList
                    if hasattr(stream.tlsSettings, 'serverName'):
                        params["sni"] = stream.tlsSettings.serverName
        if stream.network == "ws" and stream.wsSettings:
            if stream.wsSettings.path:
                params["path"] = stream.wsSettings.path
            if stream.wsSettings.headers and stream.wsSettings.headers.get(
                    'Host'):
                params["host"] = stream.wsSettings.headers['Host']
        elif stream.network == "grpc" and stream.grpcSettings:
            if stream.grpcSettings.serviceName:
                params["serviceName"] = stream.grpcSettings.serviceName
            if hasattr(stream.grpcSettings,
                       'multiMode') and stream.grpcSettings.multiMode:
                params["mode"] = "multi"
        elif stream.network == "tcp" and stream.tcpSettings:
            if stream.tcpSettings.header and stream.tcpSettings.header.get(
                    "type"):
                if stream.tcpSettings.header["type"] != 'none':
                    params["headerType"] = stream.tcpSettings.header["type"]
        elif stream.network == "kcp" and stream.kcpSettings:
            if stream.kcpSettings.header and stream.kcpSettings.header.get(
                    "type"
            ):
                params["headerType"] = stream.kcpSettings.header["type"]
            if hasattr(stream.kcpSettings, 'seed'):
                params["seed"] = stream.kcpSettings.seed
        elif stream.network == "http" and stream.httpSettings:
            if stream.httpSettings.path:
                params["path"] = ','.join(
                    stream.httpSettings.path) if isinstance(
                    stream.httpSettings.path,
                    list) else stream.httpSettings.path
            if stream.httpSettings.host:
                params["host"] = ','.join(
                    stream.httpSettings.host) if isinstance(
                    stream.httpSettings.host,
                    list) else stream.httpSettings.host
    else:
        params["type"] = "tcp"
    query_string = ""
    if params:
        query_string = "?" + urllib.parse.urlencode(params)
    if custom_remark:
        remark = custom_remark
    else:
        remark = f"{client.email}"

    fragment = "#" + urllib.parse.quote(remark, safe='')
    key_str = f"{user_base64}@{address}:{inbound.port}{query_string}{fragment}"
    return f"ss://{key_str}"
