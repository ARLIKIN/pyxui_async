import base64
import logging
from typing import Dict, Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from pyxui_async.models import Inbound


async def generate_wireguard_configs_dict(
    inbound: Inbound,
    address: str,
    dns: list[str] = ['1.1.1.1', '1.0.0.1'],
    allowed_ips: str = '0.0.0.0/0, ::/0',
    user_public_key: str = None
) -> Dict[str, str]:
    """
    Генерирует конфигурации WireGuard и возвращает их в виде словаря,
    где ключ - публичный ключ клиента, значение - конфигурация.

    Args:
        inbound: Объект InboundResponse с данными о подключении
        address: Адрес панели 3x-ui без http или https
        dns: DNS адреса по умолчанию 1.1.1.1, 1.0.0.1
        allowed_ips: Разрешенные адреса по умолчанию 0.0.0.0/0, ::/0
        user_public_key: Публичный ключ пользователя, укажите если хотите
        получить только одного пользователя.

    Returns:
        Dict[str, str]: Словарь с конфигурациями
    """
    configs = {}

    inbound = inbound.obj
    settings = inbound.settings
    server_secret_key = settings.secretKey
    port = inbound.port
    mtu = settings.mtu
    dns_str = ', '.join(dns)
    public_key = await generate_public_key(server_secret_key)

    for peer in settings.peers:
        if user_public_key is not None and user_public_key != peer.publicKey:
            continue
        config_lines = [
            "[Interface]",
            f"PrivateKey = {peer.privateKey}",
            f"Address = {peer.allowedIPs[0]}",
            f"DNS = {dns_str}",
            f"MTU = {mtu}",
            "",
            "# -1",
            "[Peer]",
            f"PublicKey = {public_key}",
            f"AllowedIPs = {allowed_ips}",
            f"Endpoint = {address}:{port}",
        ]

        if peer.preSharedKey != '':
            config_lines.append(f"PresharedKey = {peer.preSharedKey}")

        if peer.keepAlive is not None and peer.keepAlive > 0:
            config_lines.append(f"PersistentKeepalive = {peer.keepAlive}\n")

        configs[peer.publicKey] = "\n".join(config_lines)

    return configs


async def generate_public_key(private_key_b64: str) -> Optional[str]:
    """
    Генерирует публичный ключ WireGuard из приватного ключа.

    Args:
        private_key_b64: Приватный ключ в base64

    Returns:
        Публичный ключ в base64 или None в случае ошибки
    """
    try:
        private_key_bytes = base64.b64decode(private_key_b64)
        if len(private_key_bytes) != 32:
            raise ValueError(
                f"Private key must be 32 bytes, got {len(private_key_bytes)}"
            )
        private_key = X25519PrivateKey.from_private_bytes(private_key_bytes)
        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        public_key_b64 = base64.b64encode(public_key_bytes).decode('ascii')
        return public_key_b64
    except Exception as e:
        logging.error(f"Ошибка генерации публичного ключа:", exc_info=e)
        return None


async def generate_wireguard_keys() -> tuple[str, str]:
    """
    Генерирует пару ключей WireGuard (private, public)
    """
    private_key = X25519PrivateKey.generate()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    private_b64 = base64.b64encode(private_bytes).decode('ascii')
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    public_b64 = base64.b64encode(public_bytes).decode('ascii')

    return private_b64, public_b64