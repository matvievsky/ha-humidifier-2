"""Binary sensor platform for Xiaomi Humidifier 2."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([XiaomiHumidifier2NoWaterSensor(entry)])


class XiaomiHumidifier2NoWaterSensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor that is ON when the humidifier has no water."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_has_entity_name = True
    _attr_name = "No water"
    _attr_icon = "mdi:water-off"

    def __init__(self, entry: ConfigEntry) -> None:
        runtime_data = entry.runtime_data
        super().__init__(runtime_data["coordinator"])
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_no_water"

    @property
    def is_on(self) -> bool | None:
        return getattr(self.coordinator.data, "no_water", None)

    @property
    def device_info(self):
        entry = self._coordinator.config_entry
        return {
            "identifiers": {(DOMAIN, entry.unique_id or entry.entry_id)},
        }
