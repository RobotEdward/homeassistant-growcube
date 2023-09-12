"""Support for GrowCube smart plant watering sensors."""
from __future__ import annotations

from datetime import timedelta
import logging

import async_timeout
from pygrowcube import pygrowcube

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensor entities for this GrowCube config entry."""
    status = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = GrowCubeSensorCoordinator(hass, status)
    new_devices = [RoomTemperature(status, coordinator), Humidity(status, coordinator)]
    for i in range(4):
        new_devices.append(Moisture(i, status, coordinator))
    async_add_entities(new_devices)
    await coordinator.async_config_entry_first_refresh()


class GrowCubeSensorCoordinator(DataUpdateCoordinator):
    """Update Coordinator for GrowCube sensors."""

    def __init__(self, hass: HomeAssistant, my_api: pygrowcube.Status) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=f"Growcube {my_api.id}",
            # Polling interval.
            update_interval=timedelta(seconds=300),
        )
        self.status = my_api

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            _LOGGER.info("Refreshing GrowCube status")
            async with async_timeout.timeout(15):
                self.status = await pygrowcube.get_status(
                    growcube_address=self.status.host,
                    timeout_in_seconds=14,
                    wait_for_sensor_readings=True,
                )
                _LOGGER.info(
                    "GrowCube refreshed all sensors: %s",
                    self.status.is_refresh_complete,
                )
                _LOGGER.debug("GrowCube latest status: %s", str(self.status))
                return self.status
        except Exception as err:
            # This happens if user also has the GrowCube app open when the refresh runs
            # Probably better to debounce these and use previous readings unless
            # we get several failures in succession.
            raise UpdateFailed("Error communicating with GrowCube API") from err


class RoomTemperature(CoordinatorEntity, SensorEntity):
    """GrowCube room temperature sensor entity."""

    def __init__(
        self, status: pygrowcube.Status, coordinator: GrowCubeSensorCoordinator
    ) -> None:
        """Initialise the sensor from GrowCube status object."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_native_value = int(status.temperature)
        self._attr_unique_id = f"{status.id}+_temperature"
        self._attr_name = "GrowCube Temperature"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = SensorDeviceClass.TEMPERATURE

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("Update RoomTemp %s", str(self.coordinator.data))
        self._attr_native_value = self.coordinator.data.temperature
        self.async_write_ha_state()


class Humidity(CoordinatorEntity, SensorEntity):
    """GrowCube humidity sensor entity."""

    def __init__(
        self, status: pygrowcube.Status, coordinator: GrowCubeSensorCoordinator
    ) -> None:
        """Initialise the sensor from GrowCube status object."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_native_value = int(status.humidity)
        self._attr_unique_id = f"{status.id}+_humidity"
        self._attr_name = "GrowCube Humidity"
        self._attr_native_unit_of_measurement = "%"
        self._attr_device_class = SensorDeviceClass.HUMIDITY

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("Update Humidity %s", str(self.coordinator.data))
        self._attr_native_value = self.coordinator.data.humidity
        self.async_write_ha_state()


class Moisture(CoordinatorEntity, SensorEntity):
    """GrowCube moisture sensor entity - one per channel."""

    def __init__(
        self,
        channel: int,
        status: pygrowcube.Status,
        coordinator: GrowCubeSensorCoordinator,
    ) -> None:
        """Initialise the sensor from GrowCube status object and a channel number."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        outlet = ["A", "B", "C", "D"][channel]
        self._attr_native_value = int(status.moistures[channel])
        self._attr_unique_id = f"{status.id}_plant_{outlet}"
        self._attr_name = f"GrowCube Plant {outlet}"
        self._attr_native_unit_of_measurement = "%"
        self._attr_device_class = SensorDeviceClass.MOISTURE
        self.channel = channel

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("Update Sensor %s %s", self.channel, str(self.coordinator.data))
        self._attr_native_value = self.coordinator.data.moistures[self.channel]
        self.async_write_ha_state()
