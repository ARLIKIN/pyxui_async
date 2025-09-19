from typing import Union

from pyxui_async.models import InboundClientStats
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