import json
from typing import Union

import pyxui_async
from pyxui_async import errors


class Clients:
    async def get_client(
        self: "pyxui_async.XUI",
        inbound_id: int,
        email: str = False,
        uuid: str = False
    ) -> Union[dict, errors.NotFound]:
        """Get client from the existing inbound.

        Parameters:
            inbound_id (``int``):
                Inbound id
                
            email (``str``, optional):
               Email of the client
                
            uuid (``str``, optional):
               UUID of the client
            
        Returns:
            `~Dict`: On success, a dict is returned or else 404 an error will be raised
        """
        
        get_inbounds = await self.get_inbounds()
        
        if not email and not uuid:
            raise ValueError()
        
        for inbound in get_inbounds['obj']:
            if inbound['id'] != inbound_id:
                continue
            
            settings = json.loads(inbound['settings'])
            
            for client in settings['clients']:
                if client['email'] != email and client['id'] != uuid:
                    continue
                
                return client

        raise errors.NotFound()

    async def get_client_stats(
        self: "pyxui_async.XUI",
        inbound_id: int,
        email: str,
    ) -> Union[dict, errors.NotFound]:
        """Get client stats from the existing inbound.

        Parameters:
            inbound_id (``int``):
                Inbound id
                
            email (``str``):
               Email of the client
            
        Returns:
            `~Dict`: On success, a dict is returned or else 404 error will be raised
        """
        
        get_inbounds = await self.get_inbounds()
        
        if not email:
            raise ValueError()
        
        for inbound in get_inbounds['obj']:
            if inbound['id'] != inbound_id:
                continue
            
            client_stats = inbound['clientStats']
            
            for client in client_stats:
                if client['email'] != email:
                    continue
                
                return client

        raise errors.NotFound()

    async def add_client(
        self: "pyxui_async.XUI",
        inbound_id: int,
        email: str,
        uuid: str,
        enable: bool = True,
        flow: str = "",
        limit_ip: int = 0,
        total_gb: int = 0,
        expire_time: int = 0,
        telegram_id: str = "",
        subscription_id: str = "",
    ) -> Union[dict, errors.NotFound]:
        """Add client to the existing inbound.

        Parameters:
            inbound_id (``int``):
                Inbound id
                
            email (``str``):
               Email of the client
                
            uuid (``str``):
               UUID of the client
                
            enable (``bool``, optional):
               Status of the client
                
            flow (``str``, optional):
               Flow of the client
                
            limit_ip (``str``, optional):
               IP Limit of the client
                
            total_gb (``str``, optional):
                Download and uploader limition of the client and it's in bytes
                
            expire_time (``str``, optional):
                Client expiration date and it's in timestamp (epoch)
                
            telegram_id (``str``, optional):
               Telegram id of the client
                
            subscription_id (``str``, optional):
               Subscription id of the client
            
        Returns:
            `~Dict`: On success, a dict is returned else 404 error will be raised
        """

        settings = {
            "clients": [
                {
                    "id": uuid,
                    "email": email,
                    "enable": enable,
                    "flow": flow,
                    "limitIp": limit_ip,
                    "totalGB": total_gb,
                    "expiryTime": expire_time,
                    "tgId": telegram_id,
                    "subId": subscription_id
                }
            ],
            "decryption": "none",
            "fallbacks": []
        }
        
        params = {
            "id": inbound_id,
            "settings": json.dumps(settings)
        }

        return await self.request(
            path="addClient",
            method="POST",
            params=params
        )

    async def delete_client(
        self: "pyxui_async.XUI",
        inbound_id: int,
        email: str = False,
        uuid: str = False
    ) -> Union[dict, errors.NotFound]:
        """Delete client from the existing inbound.

        Parameters:
            inbound_id (``int``):
                Inbound id
                
            email (``str``, optional):
               Email of the client
                
            uuid (``str``, optional):
               UUID of the client
            
        Returns:
            `~Dict`: On success, a dict is returned else 404 error will be raised
        """
        
        find_client = await self.get_client(
            inbound_id=inbound_id,
            email=email,
            uuid=uuid
        )
        
        return await self.request(
            path=f"{inbound_id}/delClient/{find_client['id']}",
            method="POST"
        )

    async def update_client(
        self: "pyxui_async.XUI",
        inbound_id: int,
        email: str | bool = False,
        uuid: str | bool = False,
        enable: bool | None = None,
        flow: str | None = None,
        limit_ip: int | None = None,
        total_gb: int | None = None,
        expire_time: int | None = None,
        telegram_id: str | None = None,
        subscription_id: str | None = None,
    ) -> Union[dict, errors.NotFound]:
        """Add client to the existing inbound.

        Parameters:
            inbound_id (``int``):
                Inbound id
                
            email (``str``):
               Email of the client
                
            uuid (``str``):
               UUID of the client
                
            enable (``bool``):
               Status of the client
                
            flow (``str``):
               Flow of the client
                
            limit_ip (``str``):
               IP Limit of the client
                
            total_gb (``str``):
                Download and uploader limition of the client and it's in bytes
                
            expire_time (``str``):
                Client expiration date and it's in timestamp (epoch)
                
            telegram_id (``str``):
               Telegram id of the client
                
            subscription_id (``str``):
               Subscription id of the client
            
        Returns:
            `~Dict`: On success, a dict is returned else 404 error will be raised
        """
        
        find_client = await self.get_client(
            inbound_id=inbound_id,
            email=email,
            uuid=uuid
        )
        
        settings = {
            "clients": [
                {
                    "id": find_client['id'],
                    "email": find_client['email'],
                    "enable": enable if enable is not None else find_client['enable'],
                    "flow": flow if flow else find_client['flow'],
                    "limitIp": limit_ip if limit_ip else find_client['limitIp'],
                    "totalGB": total_gb if total_gb else find_client['totalGB'],
                    "expiryTime": expire_time if expire_time else find_client['expiryTime'],
                    "tgId": telegram_id if telegram_id else find_client['tgId'],
                    "subId": subscription_id if subscription_id else find_client['subId'],
                }
            ],
            "decryption": "none",
            "fallbacks": []
        }
            
        params = {
            "id": inbound_id,
            "settings": json.dumps(settings)
        }
        
        return await self.request(
            path=f"updateClient/{find_client['id']}",
            method="POST",
            params=params
        )
