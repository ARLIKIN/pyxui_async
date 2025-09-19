import json

from pyxui_async.errors import (
    NotFound,
    Duplicate,
    NoIpRecord
)
from pyxui_async.models import (
    ClientSettings,
    GenericObjResponse,
    ClientTrafficsResponse,
    POST,
    GET
)
from typing import Optional, Union


class Client:
    async def get_client_traffics_by_email(
        self,
        email: str
    ) -> Union[ClientTrafficsResponse, NotFound]:
        """
        Получить статистику трафика и информацию о клиенте по email.
        Если клиент не найден — NotFound.
        """
        result = await self.request(
            method=GET,
            endpoint=f'/panel/api/inbounds/getClientTraffics/{email}'
        )
        if result.get("obj") is None:
            raise NotFound()
        return ClientTrafficsResponse(**result)

    async def get_client_traffics_by_id(
        self,
        uuid: str
    ) -> Union[ClientTrafficsResponse, NotFound]:
        """
        Получить статистику трафика и информацию о клиенте по UUID.
        Если клиент не найден — NotFound.
        """
        result = await self.request(
            method=GET,
            endpoint=f'/panel/api/inbounds/getClientTrafficsById/{uuid}'
        )
        if result.get("obj") is None:
            raise NotFound()
        return ClientTrafficsResponse(**result)

    async def client_ips(
        self,
        email: str
    ) -> Union[GenericObjResponse, NoIpRecord]:
        """Получить IP-адреса, связанные с клиентом по email."""
        result = await self.request(
            method=POST, endpoint=f'/panel/api/inbounds/clientIps/{email}'
        )
        if result.get('obj') == 'No IP Record':
            raise NoIpRecord(email=email)
        return GenericObjResponse(**result)

    async def add_clients(
        self, inbound_id: int, client_settings: ClientSettings
    ) -> GenericObjResponse:
        """Добавить клиента(ов) к Inbound по ID."""
        settings_str = client_settings.model_dump_json()
        request_body = {
            "id": inbound_id,
            "settings": settings_str
        }
        result = await self.request(
            method=POST,
            endpoint='/panel/api/inbounds/addClient',
            json=request_body,
        )
        if 'Duplicate email' in result.get('msg'):
            raise Duplicate(message=result.get('msg'))
        return GenericObjResponse(**result)

    async def update_client(
        self,
        inbound_id: int,
        email: str,
        uuid: str | bool = False,
        enable: bool | None = None,
        flow: str | None = None,
        limit_ip: int | None = None,
        total_gb: int | None = None,
        expire_time: int | None = None,
        telegram_id: str | None = None,
        subscription_id: str | None = None,
    ) -> GenericObjResponse:
        """Обновить данные клиента в Inbound по UUID."""
        find_client = await self.get_client(inbound_id, email)
        settings = {
            "clients": [
                {
                    "id": find_client.id,
                    "email": find_client.email,
                    "enable": enable if enable is not None else
                    find_client.enable,
                    "flow": flow if flow else find_client.flow,
                    "limitIp": limit_ip if limit_ip else find_client.limitIp,
                    "totalGB": total_gb if total_gb else find_client.totalGB,
                    "expiryTime": expire_time if expire_time else
                    find_client.expiryTime,
                    "tgId": telegram_id if telegram_id else find_client.tgId,
                    "subId": subscription_id if subscription_id else
                    find_client.subId,
                }
            ],
            "decryption": "none",
            "fallbacks": []
        }
        request_body = {
            "id": inbound_id,
            "settings": json.dumps(settings)
        }
        result = await self.request(
            method=POST,
            endpoint=f"/panel/api/inbounds/updateClient/{uuid}",
            json=request_body,
        )
        return GenericObjResponse(**result)

    async def clear_client_ips(self, email: str) -> GenericObjResponse:
        """Очистить (сбросить) IP-адреса клиента по email."""
        result = await self.request(
            method=POST,
            endpoint=f"/panel/api/inbounds/clearClientIps/{email}"
        )
        return GenericObjResponse(**result)

    async def reset_client_traffic(
        self,
        inbound_id: int,
        email: str
    ) -> GenericObjResponse:
        """Сбросить трафик конкретного клиента по email и Inbound."""
        result = await self.request(
            method=POST,
            endpoint=
                f"/panel/api/inbounds/{inbound_id}/resetClientTraffic/{email}"
        )
        return GenericObjResponse(**result)

    async def delete_client_id(
        self,
        inbound_id: int,
        uuid: str
    ) -> GenericObjResponse:
        """Удалить клиента из Inbound по UUID."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/inbounds/{inbound_id}/delClient/{uuid}'
        )
        return GenericObjResponse(**result)

    async def delete_client_email(
        self,
        inbound_id: int,
        email: str
    ) -> GenericObjResponse:
        """Удалить клиента из Inbound по email."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/inbounds/{inbound_id}/delClientByEmail/{email}'
        )
        return GenericObjResponse(**result)

    async def delete_depleted_clients(
        self,
        inbound_id: Optional[int] = None
    ) -> GenericObjResponse:
        """Удалить всех исчерпанных клиентов (depleted clients) из Inbound."""
        if inbound_id is not None:
            endpoint = f'/panel/api/inbounds/delDepletedClients/{inbound_id}'
        else:
            endpoint = '/panel/api/inbounds/delDepletedClients/'
        result = await self.request(
            method=POST,
            endpoint=endpoint,
        )
        return GenericObjResponse(**result)

    async def online_clients(self) -> GenericObjResponse:
        """Получить список онлайн-клиентов."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/inbounds/onlines'
        )
        return GenericObjResponse(**result)
