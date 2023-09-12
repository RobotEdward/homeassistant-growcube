"""Config flow for GrowCube integration."""
from __future__ import annotations

import logging
from typing import Any

from pygrowcube import pygrowcube
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("ip", description="IP address of the GrowCube"): str,
    }
)

# 2023-09-05 17:26:12.053 INFO (SyncWorker_3) [pygrowcube.messageclient] RECEIVED 34 UNKNOWN: 1
# 2023-09-05 17:26:12.055 ERROR (MainThread) [homeassistant.components.growcube.config_flow] Exception while validating growcube host
# 2023-09-05 17:26:12.072 ERROR (MainThread) [homeassistant.components.growcube.config_flow] Status.default_handler() takes 2 positional arguments but 3 were given


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    try:
        status = await pygrowcube.get_status(
            growcube_address=data["ip"],
            timeout_in_seconds=5,
            wait_for_sensor_readings=False,
        )
    except Exception as ex:
        _LOGGER.error("Exception while validating growcube host")
        _LOGGER.exception(ex)
        raise CannotConnect

    _LOGGER.info("Got status %s", str(status))
    return {
        "title": "GrowCube",
        "unique_id": status.id,
        "version": status.version,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GrowCube."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
