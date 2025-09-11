from typing import Dict, Any

from pyxui_async.models import (
    GenericObjResponse,
    UUIDResponse,
    X25519CertResponse,
    Mldsa65Response,
    VlessEncResponse,
    EchCertResponse,
    POST,
    GET
)


class Server:
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
        return result

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

    async def tgbot_send_backup(self) -> str:
        """Отправить резервную копию базы через Telegram-бота администраторам."""
        result = await self.request(
            method=GET,
            endpoint=f'/panel/api/backuptotgbot'
        )
        return str(result)
