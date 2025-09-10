import urllib.parse
from typing import Optional, List

from pyxui_async.models import Inbound


async def build_vless_from_inbound(
    inbound: Inbound,
    email: str,
    address: str,
    custom_remark: Optional[str] = None,
) -> str:


    # Проверяем что это VLESS протокол
    if inbound.protocol.lower() != 'vless':
        raise ValueError(
            f"Протокол должен быть VLESS, получен: {inbound.protocol}")

    # Проверяем наличие клиентов
    if not inbound.settings.clients or len(inbound.settings.clients) == 0:
        raise ValueError("В Inbound нет клиентов")

    client = None
    for client_setting in inbound.settings.clients:
        if client_setting.email != email:
            continue
        client = client_setting

    if client is None:
        raise ValueError()

    # Базовая часть URI
    base = f"vless://{client.id}@{address}:{inbound.port}"

    # Собираем параметры
    params = {
        "encryption": "none"  # VLESS всегда использует none
    }

    # Настройки стрима
    if inbound.streamSettings:
        stream = inbound.streamSettings
        params["type"] = stream.network
        params["security"] = 'none'

        # Безопасность
        if stream.security and stream.security != "none":
            params["security"] = stream.security

        # Reality настройки
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
                params["alpn"] = stream.tlsSettings.alpn[0] + ',' + stream.tlsSettings.alpn[1]
                params["ech"] = stream.tlsSettings.settings.echConfigList

        if stream.network == "tcp" and stream.tcpSettings:
            tcp = stream.tcpSettings
            if tcp.header and tcp.header.get("type"):
                if tcp.header["type"] != 'none':
                    params["headerType"] = tcp.header["type"]

        if stream.security == "reality" and stream.realitySettings:
            if stream.realitySettings.settings['mldsa65Verify']:
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

    # URL-кодируем remark для фрагмента
    fragment = "#" + urllib.parse.quote(remark, safe='')

    return f"{base}?{query_string}{fragment}"