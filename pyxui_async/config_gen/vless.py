import urllib.parse
from typing import Optional, Union

from pyxui_async.errors import NotFound
from pyxui_async.models import Inbound


async def build_vless_from_inbound(
    inbound: Inbound,
    email: str,
    address: str,
    custom_remark: Optional[str] = None,
) -> Union[str, ValueError, NotFound]:
    """
    Собирает из данных подключения ключ пользователя Vless.
    """
    if inbound.protocol.lower() != 'vless':
        raise ValueError(
            f"The protocol must be VLESS, received: {inbound.protocol}"
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
    base = f"vless://{client.id}@{address}:{inbound.port}"
    params = {}
    if inbound.streamSettings:
        stream = inbound.streamSettings
        params["type"] = stream.network
        if inbound.settings.encryption:
            params["encryption"] = inbound.settings.encryption
        params["security"] = 'none'
        if stream.security and stream.security != "none":
            params["security"] = stream.security
        if stream.security == "reality" and stream.realitySettings:
            reality = stream.realitySettings
            params["pbk"] = reality.settings['publicKey']
            params["fp"] = reality.settings['fingerprint']
            if reality.serverNames:
                params["sni"] = reality.serverNames[0]
            if reality.shortIds:
                params["sid"] = reality.shortIds[0]
            params["spx"] = reality.settings['spiderX']
        elif stream.security == "tls":
            if stream.tlsSettings:
                params["fp"] = stream.tlsSettings.settings.fingerprint
                params["alpn"] = (
                    stream.tlsSettings.alpn[0] + ','
                    + stream.tlsSettings.alpn[1]
                )
                params["ech"] = stream.tlsSettings.settings.echConfigList
        if stream.network == "tcp" and stream.tcpSettings:
            tcp = stream.tcpSettings
            if tcp.header and tcp.header.get("type"):
                if tcp.header["type"] != 'none':
                    params["headerType"] = tcp.header["type"]
        if stream.security == "reality" and stream.realitySettings:
            if stream.realitySettings.settings.get('mldsa65Verify'):
                params["pqv"] = stream.realitySettings.settings['mldsa65Verify']
            if client.flow:
                params["flow"] = client.flow
    else:
        params["type"] = "tcp"
    query_string = urllib.parse.urlencode(params)
    if custom_remark:
        remark = custom_remark
    else:
        remark = f"{client.email}"
    fragment = "#" + urllib.parse.quote(remark, safe='')
    return f"{base}?{query_string}{fragment}"
