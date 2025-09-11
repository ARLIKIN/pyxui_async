from typing import Union

from pyxui_async.errors import NotFound
from pyxui_async.models import (
    InboundsResponse,
    GET,
    InboundResponse,
    InboundRequest,
    GenericObjResponse,
    POST
)


class Inbounds:
    async def get_inbounds(self) -> InboundsResponse:
        """Получить список всех Inbound-правил (входящих соединений)."""
        result = await self.request(
            method=GET, endpoint='/panel/api/inbounds/list'
        )
        return InboundsResponse(**result)

    async def get_inbound(
            self, inbound_id: int
    ) -> Union[InboundResponse, NotFound]:
        """
        Получить подробную информацию по-конкретному Inbound по его ID.
        Если не найден — NotFound.
        """
        result = await self.request(
            method=GET, endpoint=f'/panel/api/inbounds/get/{inbound_id}'
        )
        if not result.get("success", False) or result.get("obj") is None:
            raise NotFound()
        return InboundResponse(**result)

    async def add_inbound(self, inbound: InboundRequest) -> GenericObjResponse:
        """Добавить Inbound."""
        body = inbound.model_dump()
        body['settings'] = inbound.settings.model_dump_json()
        if inbound.streamSettings:
            body['streamSettings'] = inbound.streamSettings.model_dump_json()
        if inbound.sniffing:
            body['sniffing'] = inbound.sniffing.model_dump_json()
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/inbounds/add',
            json=body,
        )
        return GenericObjResponse(**result)

    async def delete_inbound(self, inbound_id: int) -> GenericObjResponse:
        """Удалить Inbound по его ID."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/inbounds/del/{inbound_id}',
        )
        return GenericObjResponse(**result)

    async def update_inbound(
        self,
        inbound_id: int,
        inbound: InboundRequest
    ) -> GenericObjResponse:
        """Обновить существующий Inbound по ID."""
        body = inbound.model_dump()
        body["settings"] = inbound.settings.model_dump_json()
        if inbound.streamSettings:
            body["streamSettings"] = inbound.streamSettings.model_dump_json()
        if inbound.sniffing:
            body["sniffing"] = inbound.sniffing.model_dump_json()
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/inbounds/update/{inbound_id}',
            json=body,
        )
        return GenericObjResponse(**result)

    async def reset_all_traffics(self) -> GenericObjResponse:
        """Сбросить статистику трафика по всем Inbound."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/inbounds/resetAllTraffics'
        )
        return GenericObjResponse(**result)

    async def reset_all_client_traffics(
        self,
        inbound_id: int
    ) -> GenericObjResponse:
        """Сбросить трафик всех клиентов конкретного Inbound."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/inbounds/resetAllClientTraffics/{inbound_id}'
        )
        return GenericObjResponse(**result)

    async def import_inbound(
        self,
        inbound: InboundRequest
    ) -> GenericObjResponse:
        """Импортировать Inbound-конфигурацию."""
        body = inbound.model_dump()
        body["settings"] = inbound.settings.model_dump_json()
        if inbound.streamSettings:
            body["streamSettings"] = inbound.streamSettings.model_dump_json()
        if inbound.sniffing:
            body["sniffing"] = inbound.sniffing.model_dump_json()
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/inbounds/import',
            json=body,
        )
        return GenericObjResponse(**result)
