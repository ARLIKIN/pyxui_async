from typing import Union

from pyxui_async.config_gen.vless import build_vless_from_inbound
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

    async def get_key_vless(self, inbound_id, email) -> str:
        inbound = await self.get_inbound(inbound_id)
        domain = self.get_domain()
        return await build_vless_from_inbound(inbound.obj, email, domain)