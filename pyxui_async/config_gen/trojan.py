import urllib.parse
from typing import Optional, Union

from pyxui_async.errors import NotFound
from pyxui_async.models import Inbound


async def build_trojan_from_inbound(
    inbound: Inbound,
    email,
    address: str,
    custom_remark: Optional[str] = None,
) -> Union[str, ValueError, NotFound]:
    if inbound.protocol.lower() != 'trojan':
        raise ValueError(f"The protocol must be TROJAN, received: {inbound.protocol}")
    client = None
    for client_setting in inbound.settings.clients:
        if client_setting.email != email:
            continue
        client = client_setting

    if client is not None:
        if getattr(client, "password", None):
            used_password = client.password
        elif getattr(client, "id", None):
            used_password = client.id
        else:
            raise ValueError('password is None')
    else:
        raise ValueError('client is None')

    base = f"trojan://{used_password}@{address}:{inbound.port}"
    params = {}

    if inbound.streamSettings:
        stream = inbound.streamSettings
        params["type"] = getattr(stream, "network", "tcp") or "tcp"
        if getattr(inbound.settings, "encryption", None):
            params["encryption"] = inbound.settings.encryption

        # default security
        params["security"] = "none"
        if getattr(stream, "security", None) and stream.security != "none":
            params["security"] = stream.security

        # reality
        if stream.security == "reality" and getattr(stream, "realitySettings", None):
            reality = stream.realitySettings
            if reality.settings and isinstance(reality.settings, dict):
                if reality.settings.get("publicKey"):
                    params["pbk"] = reality.settings["publicKey"]
                if reality.settings.get("fingerprint"):
                    params["fp"] = reality.settings["fingerprint"]
            if getattr(reality, "serverNames", None):
                params["sni"] = reality.serverNames[0]
            if getattr(reality, "shortIds", None):
                params["sid"] = reality.shortIds[0]
            if reality.settings.get("spiderX") is not None:
                params["spx"] = str(reality.settings["spiderX"])
            if (reality.settings.get("mldsa65Verify") is not None
                    and reality.settings.get("mldsa65Verify") != ''):
                params["pqv"] = str(reality.settings["mldsa65Verify"])
        # tls
        elif stream.security == "tls":
            if getattr(stream, "tlsSettings", None):
                tls = stream.tlsSettings
                fp_candidate = None
                if getattr(tls, "settings", None):
                    settings = tls.settings
                    if isinstance(settings, dict):
                        fp_candidate = settings.get("fingerprint")
                        ech_candidate = settings.get("echConfigList")
                    else:
                        fp_candidate = getattr(settings, "fingerprint", None)
                        ech_candidate = getattr(settings, "echConfigList", None)
                else:
                    ech_candidate = None

                if fp_candidate:
                    params["fp"] = fp_candidate
                if getattr(tls, "alpn", None):
                    try:
                        params["alpn"] = ",".join(str(x) for x in tls.alpn)
                    except Exception:
                        params["alpn"] = str(tls.alpn)
                if ech_candidate:
                    if isinstance(ech_candidate, (list, tuple)):
                        params["ech"] = ",".join(str(x) for x in ech_candidate)
                    else:
                        params["ech"] = str(ech_candidate)
                if getattr(tls, "serverName", None):
                    params["sni"] = tls.serverName
        if stream.network == "tcp" and getattr(stream, "tcpSettings", None):
            tcp = stream.tcpSettings
            header = getattr(tcp, "header", None) or {}
            if isinstance(header, dict):
                htype = header.get("type")
                if htype and htype != "none":
                    params["headerType"] = htype
        if client is not None and getattr(client, "flow", None):
            params["flow"] = client.flow
    else:
        params["type"] = "tcp"
    str_params = {}
    for k, v in params.items():
        if v is None:
            continue
        if isinstance(v, bytes):
            try:
                v = v.decode()
            except Exception:
                v = str(v)
        if isinstance(v, (list, tuple)):
            v = ",".join(str(x) for x in v)
        str_params[k] = str(v)
    query_string = urllib.parse.urlencode(str_params, quote_via=urllib.parse.quote)
    if custom_remark:
        remark = custom_remark
    else:
        if client is not None and getattr(client, "email", None):
            remark = client.email
        else:
            short_pwd = used_password if len(used_password) <= 8 else used_password[:8]
            remark = f"{short_pwd}@{address}:{inbound.port}"

    fragment = "#" + urllib.parse.quote(remark, safe='')
    if query_string:
        return f"{base}?{query_string}{fragment}"
    else:
        return f"{base}{fragment}"
