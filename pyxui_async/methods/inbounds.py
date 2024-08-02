from typing import Union

import pyxui_async
from pyxui_async import errors


class Inbounds:
    async def get_inbounds(
        self: "pyxui_async.XUI"
    ) -> Union[dict, errors.NotFound]:
        """Get inbounds of the xui panel.
        
        Returns:
            `~Dict | errors.NotFound`: On success, a dict is returned else 404 error will be raised
        """
        if self.panel == "alireza":
            path = ""
            
        elif self.panel == "sanaei":
            path = "list"
        
        response = await self.request(
            path=path,
            method="GET"
        )

        return await self.verify_response(response)
        
    async def get_inbound(
        self: "pyxui_async.XUI",
        inbound_id: int
    ) -> Union[dict, errors.NotFound]:
        """Get inbounds of the xui panel.

        Parameters:
            inbound_id (``int``):
                Inbound id
        
        Returns:
            `~Dict | errors.NotFound`: On success, a dict is returned else 404 error will be raised
        """
        
        response = await self.request(
            path=f"get/{inbound_id}",
            method="GET"
        )

        return await self.verify_response(response)
