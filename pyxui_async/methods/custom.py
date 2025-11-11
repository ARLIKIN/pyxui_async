import ipaddress
import logging
from typing import Union, Dict

from pyxui_async.config_gen.wireguard import (
    generate_wireguard_configs_dict,
    generate_wireguard_keys
)
from pyxui_async.models import (
    InboundClientStats,
    WireGuardPeer,
    InboundRequest,
    SniffingSettings
)
from pyxui_async.config_gen import build_vless_from_inbound
from pyxui_async.config_gen.shadowsocks import build_shadowsocks_from_inbound
from pyxui_async.config_gen.trojan import build_trojan_from_inbound
from pyxui_async.errors import NotFound
from pyxui_async.models import Client, GenericObjResponse


class Custom:
    async def delete_client(
        self,
        inbound_id: int,
        email: str | None = None,
        uuid: str | None = None,
    ) -> GenericObjResponse:
        """Удалить клиента из Inbound по UUID или по email."""
        if email is not None:
            try:
                return await self.delete_client_email(inbound_id, email)
            except NotFound:
                client = await self.get_client(inbound_id, email)
                return await self.delete_client_id(inbound_id, client.id)
        elif uuid is not None:
            return await self.delete_client_id(inbound_id, uuid)
        else:
            raise ValueError()

    async def get_client(
        self: "XUI",
        inbound_id: int,
        email: str,
    ) -> Union[Client, NotFound]:
        if not email:
            raise ValueError()

        inbound = await self.get_inbound(inbound_id)
        for client in inbound.obj.settings.clients:
            if client.email != email:
                continue
            return client
        raise NotFound()

    async def get_client_stat(
        self: "XUI",
        inbound_id: int,
        email: str,
    ) -> Union[InboundClientStats, NotFound]:
        if not email:
            raise ValueError()
        inbounds = await self.get_inbounds()
        for inbound in inbounds.obj:
            if inbound.id == inbound_id:
                for client in inbound.clientStats:
                    if client.email != email:
                        continue
                    return client
        raise NotFound()

    async def get_key_vless(self, inbound_id, email, custom_remark=None) -> str:
        inbound = await self.get_inbound(inbound_id)
        domain = self.get_domain()
        return await build_vless_from_inbound(
            inbound.obj, email, domain, custom_remark
        )

    async def get_key_trojan(self, inbound_id, email, custom_remark=None) -> str:
        inbound = await self.get_inbound(inbound_id)
        domain = self.get_domain()
        return await build_trojan_from_inbound(
            inbound.obj, email, domain, custom_remark
        )


    async def get_key_shadow_socks(
            self, inbound_id, email, custom_remark=None
    ) -> str:
        inbound = await self.get_inbound(inbound_id)
        domain = self.get_domain()
        return await build_shadowsocks_from_inbound(
            inbound.obj, email, domain, custom_remark
        )

    async def get_keys_wg(
        self,
        inbound_id,
        dns: list[str] = ['1.1.1.1', '1.0.0.1'],
        allowed_ips: str = '0.0.0.0/0, ::/0'
    ) -> Dict[str, str]:
        inbound = await self.get_inbound(inbound_id)
        domain = self.get_domain()
        return await generate_wireguard_configs_dict(
            inbound, domain, dns, allowed_ips
        )

    async def get_key_client_wg(
        self,
        inbound_id,
        user_public_key: str,
        dns: list[str] = ['1.1.1.1', '1.0.0.1'],
        allowed_ips: str = '0.0.0.0/0, ::/0'
    ) -> Dict[str, str]:
        inbound = await self.get_inbound(inbound_id)
        domain = self.get_domain()
        return await generate_wireguard_configs_dict(
            inbound, domain, dns, allowed_ips, user_public_key
        )

    async def add_client_wg(
        self,
        inbound_id,
        preSharedKey: str = ''
    ) -> None:
        inbound = await self.get_inbound(inbound_id=inbound_id)
        private_key, public_key = await generate_wireguard_keys()
        allowed_ips = await self._get_next_allowed_ip(inbound.obj.settings.peers)
        new_peer = WireGuardPeer(
            privateKey=private_key,
            publicKey=public_key,
            preSharedKey=preSharedKey,
            allowedIPs=[allowed_ips],
            keepAlive=0
        )
        new_inbound = InboundRequest(
            up=inbound.obj.up,
            down=inbound.obj.down,
            total=inbound.obj.total,
            remark=inbound.obj.remark,
            enable=inbound.obj.enable,
            expiryTime=inbound.obj.expiryTime,
            listen=inbound.obj.listen,
            port=inbound.obj.port,
            protocol=inbound.obj.protocol,
            settings=inbound.obj.settings,
            streamSettings=inbound.obj.streamSettings,
            sniffing=SniffingSettings(
                enabled=inbound.obj.sniffing.enabled,
                destOverride=inbound.obj.sniffing.destOverride,
                metadataOnly=inbound.obj.sniffing.metadataOnly,
                routeOnly=inbound.obj.sniffing.routeOnly
            ),
        )
        new_inbound.settings.peers.append(new_peer)
        result = await self.update_inbound(
            inbound_id=inbound_id,
            inbound=new_inbound
        )
        return {
            'result': result,
            'new_peer': new_peer,
        }

    async def _get_next_allowed_ip(self, peers):
        """
        Находит следующий свободный IP (минимальный, начиная с 10.0.0.2),
        учитывая, что allowedIPs могут быть в виде /24, но занимают
        только конкретный IP, а не всю подсеть.
        """
        if not peers:
            return '10.0.0.2/32'
        used_ips = set()
        cidr_mask = None
        for peer in peers:
            for allowed_ip in peer.allowedIPs:
                net = ipaddress.ip_network(allowed_ip, strict=False)
                ip = ipaddress.ip_interface(allowed_ip).ip
                used_ips.add(ip)
                if cidr_mask is None:
                    cidr_mask = net.prefixlen
        if cidr_mask is None:
            cidr_mask = 32
        candidate = ipaddress.IPv4Address('10.0.0.2')
        while candidate in used_ips:
            candidate += 1
        return f"{candidate}/{cidr_mask}"

    async def delete_client_wg(self, inbound_id, user_public_key):
        inbound = await self.get_inbound(inbound_id=inbound_id)
        new_inbound = InboundRequest(
            up=inbound.obj.up,
            down=inbound.obj.down,
            total=inbound.obj.total,
            remark=inbound.obj.remark,
            enable=inbound.obj.enable,
            expiryTime=inbound.obj.expiryTime,
            listen=inbound.obj.listen,
            port=inbound.obj.port,
            protocol=inbound.obj.protocol,
            settings=inbound.obj.settings,
            streamSettings=inbound.obj.streamSettings,
            sniffing=SniffingSettings(
                enabled=inbound.obj.sniffing.enabled,
                destOverride=inbound.obj.sniffing.destOverride,
                metadataOnly=inbound.obj.sniffing.metadataOnly,
                routeOnly=inbound.obj.sniffing.routeOnly
            ),
        )
        peers = []
        for peer in inbound.obj.settings.peers:
            if peer.publicKey != user_public_key:
                peers.append(peer)
        new_inbound.settings.peers = peers
        result = await self.update_inbound(
            inbound_id=inbound_id,
            inbound=new_inbound
        )
        return result


    async def get_subscription_link(
        self,
        inbound_id,
        email,
        https: bool | None = None,
        port: int = 2096,
        sub_path: str = '/sub/'
    ) -> Union[str, ValueError]:
        """
        Получение ссылки подписки
        :param inbound_id: ID подключения
        :param email: email клиента
        :param https: Если вы хотите явно указать использовать https или нет
        :param port: порт подписки (указывается в настройках)
        :param sub_path: Корневой путь URL-адреса подписки (Указывается в настройках)
        :return: url or ValueError
        """
        if https is None:
            https = self.https
        client = await self.get_client(inbound_id, email)
        if client.subId is None:
            raise ValueError('Client subID not found')
        domain = self.get_domain()
        if https:
            return f'https://{domain}:{port}{sub_path}{client.subId}'
        else:
            return f'http://{domain}:{port}{sub_path}{client.subId}'