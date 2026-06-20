"""Switch platform for Xiaomi Humidifier 2 (LED light)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    async_add_entities([XiaomiHumidifier2LedSwitch(entry), XiaomiHumidifier2BuzzerSwitch(entry)])


class XiaomiHumidifier2LedSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to control the humidifier LED light."""

    _attr_has_entity_name = True
    _attr_name = "LED"
    _attr_icon = "mdi:led-outline"
    _attr_entity_registry_visible_default = True

    def __init__(self, entry: ConfigEntry) -> None:
        runtime_data = entry.runtime_data
        super().__init__(runtime_data["coordinator"])
        self._client = runtime_data["client"]
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_led"

    @property
    def is_on(self) -> bool | None:
        return getattr(self.coordinator.data, "led_light", None)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(self._client.set_led_light, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(self._client.set_led_light, False)
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        entry = self.coordinator.config_entry
        return {"identifiers": {(DOMAIN, entry.unique_id or entry.entry_id)}}


class XiaomiHumidifier2BuzzerSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "Buzzer"
    _attr_icon = "mdi:volume-high"

    def __init__(self, entry: ConfigEntry) -> None:
        runtime_data = entry.runtime_data
        super().__init__(runtime_data["coordinator"])
        self._client = runtime_data["client"]
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_buzzer"

    @property
    def is_on(self) -> bool | None:
        return getattr(self.coordinator.data, "buzzer", None)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(self._client.set_buzzer, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(self._client.set_buzzer, False)
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        entry = self.coordinator.config_entry
        return {"identifiers": {(DOMAIN, entry.unique_id or entry.entry_id)}}
