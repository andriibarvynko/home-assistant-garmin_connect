"""Binary sensor platform for Garmin Connect integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DATA_COORDINATOR, DOMAIN as GARMIN_DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Garmin Connect binary sensors."""
    coordinator: DataUpdateCoordinator = hass.data[GARMIN_DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    unique_id = entry.data[CONF_ID]

    async_add_entities([GarminConnectSleepingBinarySensor(coordinator, unique_id)])


class GarminConnectSleepingBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of the sleeping-now binary sensor."""

    _attr_has_entity_name = True
    _attr_name = "Sleeping"
    _attr_icon = "mdi:sleep"

    def __init__(self, coordinator: DataUpdateCoordinator, unique_id: str) -> None:
        super().__init__(coordinator)
        self._unique_id = unique_id
        self._attr_unique_id = f"{self._unique_id}_sleeping_now"

    @property
    def is_on(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("sleepingNow")

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        return {
            "last_synced": self.coordinator.data.get("lastSyncTimestampGMT"),
            "sleep_start": self.coordinator.data.get("sleepStart"),
            "sleep_end": self.coordinator.data.get("sleepEnd"),
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(GARMIN_DOMAIN, self._unique_id)},
            name="Garmin Connect",
            manufacturer="Garmin",
            model="Garmin Connect",
            entry_type=None,
        )

    @property
    def entity_registry_enabled_default(self) -> bool:
        return True

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.coordinator.data
            and "sleepingNow" in self.coordinator.data
        )
