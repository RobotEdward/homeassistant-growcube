"""The GrowCube integration."""
from __future__ import annotations

from pygrowcube import pygrowcube

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GrowCube from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    status = await hass.async_add_executor_job(
        pygrowcube.get_status, entry.data["ip"], 5, False
    )

    hass.data[DOMAIN][entry.entry_id] = status
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, status.id)},
        name=f"GrowCube {status.id}",
        manufacturer="Elecrow",
        model="GrowCube",
        sw_version=status.version,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
