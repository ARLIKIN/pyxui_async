import json

from pyxui_async.base import Base
from pyxui_async.config_gen.vless import build_vless_from_inbound
from pyxui_async.errors import (
    BadLogin,
    AlreadyLogin,
    NotFound,
    Duplicate,
    NoIpRecord
)
from pyxui_async.models import (
    ClientSettings,
    Client,
    InboundRequest,
    GenericObjResponse,
    ResponseBase,
    InboundsResponse,
    InboundResponse,
    ClientTrafficsResponse,
    UUIDResponse,
    X25519CertResponse,
    Mldsa65Response,
    VlessEncResponse,
    EchCertResponse,
    POST,
    GET
)
from typing import Optional, Dict, Any, Union


class XUI(Base):
    async def login(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> Union[ResponseBase, BadLogin, AlreadyLogin]:
        """
        Авторизация пользователя в панели XUI.
        Генерирует исключение BadLogin, если логин или пароль неверны.
        Генерирует исключение AlreadyLogin, если пользователь уже авторизован.
        """
        if self._session is not None:
            raise AlreadyLogin()
        data = {
            'username': username or self.username,
            'password': password or self.password
        }
        result = await self.request(
            method=POST, endpoint='/login/', data=data
        )
        if result.get('success', False):
            return ResponseBase(**result)
        raise BadLogin()

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
        for client in client_settings.clients:
            if client.id == '':
                new_id = await self.get_new_uuid()
                client.id = new_id.obj.uuid
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

    async def delete_inbound(self, inbound_id: int) -> GenericObjResponse:
        """Удалить Inbound по его ID."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/inbounds/del/{inbound_id}',
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

    async def status(self) -> GenericObjResponse:
        """Получить статус сервера."""
        result = await self.request(
            method=GET,
            endpoint=f'/panel/api/server/status'
        )
        return GenericObjResponse(**result)

    async def get_db(self) -> GenericObjResponse:
        """Получить базу данных сервера."""
        result = await self.request(
            method=GET,
            endpoint=f'/panel/api/server/getDb'
        )
        return GenericObjResponse(**result)

    async def get_xray_version(self) -> GenericObjResponse:
        """Получить список версий Xray, доступных для установки."""
        result = await self.request(
            method=GET,
            endpoint=f'/panel/api/server/getXrayVersion'
        )
        return GenericObjResponse(**result)

    async def get_config_json(self) -> GenericObjResponse:
        """Получить текущий конфиг Xray в формате JSON."""
        result = await self.request(
            method=GET,
            endpoint=f'/panel/api/server/getConfigJson'
        )
        return GenericObjResponse(**result)

    async def get_new_uuid(self) -> UUIDResponse:
        """Получить новый уникальный идентификатор UUID."""
        result = await self.request(
            method=GET,
            endpoint='/panel/api/server/getNewUUID'
        )
        return UUIDResponse(**result)

    async def get_new_x25519_cert(self) -> X25519CertResponse:
        """Получить новые ключи X25519 для конфигурации Xray."""
        result = await self.request(
            method=GET,
            endpoint=f'/panel/api/server/getNewX25519Cert'
        )
        return X25519CertResponse(**result)

    async def get_new_mldsa65(self) -> Mldsa65Response:
        """Получить новые ключи mldsa65 для конфигурации Xray."""
        result = await self.request(
            method=GET,
            endpoint=f'/panel/api/server/getNewmldsa65'
        )
        return Mldsa65Response(**result)

    async def get_new_mlkem768(self) -> Mldsa65Response:
        """Получить новые ключи ML-KEM-768 для конфигурации Xray."""
        result = await self.request(
            method=GET,
            endpoint=f'/panel/api/server/getNewmlkem768'
        )
        return Mldsa65Response(**result)

    async def get_new_vless_enc(self) -> VlessEncResponse:
        """Получить список алгоритмов шифрования VLESS для Xray."""
        result = await self.request(
            method=GET,
            endpoint=f'/panel/api/server/getNewVlessEnc'
        )
        return VlessEncResponse(**result)

    async def stop_xray_service(self) -> GenericObjResponse:
        """Остановить сервис Xray."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/server/stopXrayService'
        )
        return GenericObjResponse(**result)

    async def restart_xray_service(self) -> GenericObjResponse:
        """Перезапустить сервис Xray."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/server/restartXrayService'
        )
        return GenericObjResponse(**result)

    async def install_xray_version(self, version: str) -> GenericObjResponse:
        """Установить выбранную версию Xray на сервер."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/server/installXray/{version}'
        )
        return GenericObjResponse(**result)

    async def update_geofile(self) -> GenericObjResponse:
        """Обновить геофайл сервера."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/server/updateGeofile'
        )
        return GenericObjResponse(**result)

    async def update_geofile_name(self, file_name: str) -> GenericObjResponse:
        """Обновить геофайл сервера по имени файла."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/server/updateGeofile/{file_name}'
        )
        return GenericObjResponse(**result)

    async def logs(self, count: int) -> GenericObjResponse:
        """Получить логи сервера (последние записи)."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/server/logs/{count}'
        )
        return GenericObjResponse(**result)

    async def xraylogs(self, count: int) -> GenericObjResponse:
        """Получить логи Xray (последние записи)."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/server/xraylogs/{count}'
        )
        return GenericObjResponse(**result)

    async def import_db(self, db_data: Dict[str, Any]) -> GenericObjResponse:
        """Импортировать базу данных сервера."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/server/importDB',
            json=db_data
        )
        return GenericObjResponse(**result)

    async def get_new_ech_cert(self) -> EchCertResponse:
        """Получить новые ECH сертификаты для конфигурации Xray."""
        result = await self.request(
            method=POST,
            endpoint=f'/panel/api/server/getNewEchCert'
        )
        return EchCertResponse(**result)

    async def tgbot_send_backup(self) -> GenericObjResponse:
        """Отправить резервную копию базы через Telegram-бота администраторам."""
        result = await self.request(
            method=GET,
            endpoint=f'/panel/api/backuptotgbot'
        )
        return GenericObjResponse(**result)

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


    async def get_key_vless(self, inbound_id, email, address) -> str:
        inbound = await self.get_inbound(inbound_id)
        return await build_vless_from_inbound(inbound.obj, email, address)