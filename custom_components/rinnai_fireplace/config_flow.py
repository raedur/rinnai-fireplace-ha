"""Adds config flow for RinnaiFireplace."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries, data_entry_flow

from .api import (
    RinnaiFireplaceApiClient,
)
from .const import CONF_DEVICE_NAME, CORE_DEVICE_NAME, DOMAIN, CONF_ID, CONF_IP
from .discovery import FoundDevice, discover


class RinnaiFireplaceFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for RinnaiFireplace."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> data_entry_flow.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            if user_input["configure_type"] == "Discovery":
                return await self.async_step_discovery()
            return await self.async_step_manual()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("configure_type"): vol.In(["Discovery", "Manual"])}
            ),
            errors=_errors,
        )

    async def async_step_discovery(
        self, user_input: dict | list[FoundDevice] | None = None
    ):
        if isinstance(user_input, list):
            usable_devices = user_input

            if len(usable_devices) == 0:
                return self.async_show_form(
                    step_id="discovery",
                    data_schema=vol.Schema({}),
                    errors={
                        "base": "No Rinnai Fireplaces found. Press submit to continue with manual discovery."
                    },
                )

            return await self.async_step_configure(usable_devices)

        task = self.hass.async_create_task(discover(self.hass), f"{DOMAIN}_discovery")

        try:
            devices = await task
        except Exception:
            return self.async_abort(reason="discovery_failed")
        return await self.async_step_discovery(user_input=devices)

    async def async_step_manual(self, user_input=None):
        """Manual Discovery."""
        if user_input is None:
            return self.async_show_form(
                step_id="manual",
                data_schema=vol.Schema(
                    {
                        vol.Required("ip_address"): str,
                    }
                ),
            )

        if "ip_address" in user_input:
            api = RinnaiFireplaceApiClient(user_input["ip_address"])
            name = await api.async_get_name()
            del api
            """TODO handle timeout"""
            device = FoundDevice(None, name, user_input["ip_address"])

            return await self.async_step_configure([device])

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema(
                {
                    vol.Required("ip_address"): str,
                }
            ),
        )

    async def async_step_configure(self, user_input: list[FoundDevice] | None = None):
        """Configure Rinnai Fireplace entries."""
        if not isinstance(user_input, list) or len(user_input) == 0:
            return self.async_abort(reason="no_devices_found")

        # for now just do the first device
        device = user_input[0]

        # set unique id
        await self.async_set_unique_id(device.ip)
        self._abort_if_unique_id_configured()

        # for some reason theres no way to register multiple discovered devices so we're doing the first one that's discovered
        return self.async_create_entry(
            title=CORE_DEVICE_NAME.format(name=device.name),
            data={
                CONF_ID: device.id,
                CONF_IP: device.ip,
                CONF_DEVICE_NAME: device.name,
            },
        )
