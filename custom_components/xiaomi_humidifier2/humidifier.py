"""Humidifier platform for Xiaomi Humidifier 2."""

from __future__ import annotations

from enum import Enum
from typing import Any

from homeassistant.components.humidifier import (
    HumidifierAction,
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, is_deerma_model, is_miot_model


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the humidifier entity from a config entry."""

    async_add_entities([XiaomiHumidifier2Entity(entry)])


class XiaomiHumidifier2Entity(CoordinatorEntity, HumidifierEntity):
    """Representation of a Xiaomi Humidifier 2."""

    _attr_device_class = HumidifierDeviceClass.HUMIDIFIER
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the entity."""

        runtime_data = entry.runtime_data
        super().__init__(runtime_data["coordinator"])

        self._entry = entry
        self._client = runtime_data["client"]
        self._info = runtime_data["info"]
        self._model = runtime_data["model"]

        self._attr_unique_id = entry.unique_id or entry.entry_id
        self._attr_name = None
        self._attr_supported_features = HumidifierEntityFeature.MODES

    @property
    def available_modes(self) -> list[str]:
        """Return the available operating modes."""

        if is_deerma_model(self._model):
            return ["low", "mid", "humidity"]

        if is_miot_model(self._model):
            return ["auto", "low", "mid", "high"]

        return ["silent", "medium", "high", "auto"]

    @property
    def mode(self) -> str | None:
        """Return the current mode."""

        mode = getattr(self.coordinator.data, "mode", None)
        if mode is None:
            return None

        return self._enum_to_mode(mode)

    @property
    def is_on(self) -> bool | None:
        """Return whether the humidifier is on."""

        return getattr(self.coordinator.data, "is_on", None)

    @property
    def action(self) -> HumidifierAction | None:
        """Return the current humidifier action."""

        if not self.is_on:
            return HumidifierAction.OFF

        current = self.current_humidity
        target = self.target_humidity
        if current is not None and target is not None and current >= target and self.mode == "auto":
            return HumidifierAction.IDLE

        return HumidifierAction.HUMIDIFYING

    @property
    def current_humidity(self) -> int | None:
        """Return the measured humidity."""

        return getattr(self.coordinator.data, "humidity", None)

    @property
    def target_humidity(self) -> int | None:
        """Return the target humidity."""

        return getattr(self.coordinator.data, "target_humidity", None)

    @property
    def target_humidity_step(self) -> int:
        """Return the target humidity step."""

        return 10 if (not is_miot_model(self._model) and not is_deerma_model(self._model)) else 1

    @property
    def min_humidity(self) -> int:
        """Return minimum supported humidity."""

        return 40 if is_deerma_model(self._model) else 30

    @property
    def max_humidity(self) -> int:
        """Return maximum supported humidity."""

        return 80

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""

        data = self.coordinator.data
        attributes: dict[str, Any] = {
            "model": self._model,
            ATTR_TEMPERATURE: getattr(data, "temperature", None),
            "water_level": getattr(data, "water_level", None),
            "water_tank_detached": getattr(data, "water_tank_detached", None),
            "child_lock": getattr(data, "child_lock", None),
            "buzzer": getattr(data, "buzzer", None),
            "dry_mode": getattr(data, "dry", None),
            "led_brightness": self._enum_to_mode(getattr(data, "led_brightness", None)),
            "motor_speed": getattr(data, "motor_speed", None),
            "use_time": getattr(data, "use_time", None),
        }

        actual_speed = getattr(data, "actual_speed", None)
        if actual_speed is not None:
            attributes["actual_speed"] = actual_speed

        clean_mode = getattr(data, "clean_mode", None)
        if clean_mode is not None:
            attributes["clean_mode"] = clean_mode

        power_time = getattr(data, "power_time", None)
        if power_time is not None:
            attributes["power_time"] = power_time

        return {key: value for key, value in attributes.items() if value is not None}

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information for Home Assistant."""

        connections = set()
        if self._info.mac_address:
            connections.add((CONNECTION_NETWORK_MAC, self._info.mac_address))

        return {
            "identifiers": {(DOMAIN, self._entry.unique_id or self._entry.entry_id)},
            "connections": connections,
            "manufacturer": "Xiaomi",
            "model": self._model,
            "name": self._entry.title,
            "hw_version": self._info.hardware_version,
            "sw_version": self._info.firmware_version,
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the humidifier on."""

        await self.hass.async_add_executor_job(self._client.on)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the humidifier off."""

        await self.hass.async_add_executor_job(self._client.off)
        await self.coordinator.async_request_refresh()

    async def async_set_humidity(self, humidity: int) -> None:
        """Set the target humidity."""

        humidity = max(self.min_humidity, min(self.max_humidity, humidity))
        if not is_miot_model(self._model):
            humidity = int(round(humidity / 10) * 10)

        await self.hass.async_add_executor_job(self._client.set_target_humidity, humidity)
        await self.coordinator.async_request_refresh()

    async def async_set_mode(self, mode: str) -> None:
        """Set the humidifier mode."""

        enum_value = self._mode_to_enum(mode)
        await self.hass.async_add_executor_job(self._client.set_mode, enum_value)
        await self.coordinator.async_request_refresh()

    def _enum_to_mode(self, value: Enum | None) -> str | None:
        """Convert a device enum value into an HA mode string."""

        if value is None:
            return None

        return value.name.lower()

    def _mode_to_enum(self, mode: str) -> Enum:
        """Convert an HA mode string into a device enum."""

        if is_deerma_model(self._model):
            from .deerma_jsq04 import OperationMode as DeermaOperationMode

            modes = {item.name.lower(): item for item in DeermaOperationMode}
            return modes[mode]

        if is_miot_model(self._model):
            from miio.integrations.humidifier.zhimi.airhumidifier_miot import (
                OperationMode as MiotOperationMode,
            )

            modes = {item.name.lower(): item for item in MiotOperationMode}
            return modes[mode]

        from miio.integrations.humidifier.zhimi.airhumidifier import (
            OperationMode as LegacyOperationMode,
        )

        return LegacyOperationMode(mode)
