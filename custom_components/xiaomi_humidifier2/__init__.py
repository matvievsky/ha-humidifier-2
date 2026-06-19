"""The Xiaomi Humidifier 2 integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .coordinator import XiaomiHumidifier2Coordinator
from .device import CannotConnectError, validate_input

PLATFORMS: list[Platform] = [Platform.HUMIDIFIER, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xiaomi Humidifier 2 from a config entry."""

    try:
        runtime_data = await hass.async_add_executor_job(validate_input, entry.data)
    except CannotConnectError as err:
        raise ConfigEntryNotReady("Unable to connect to Xiaomi humidifier") from err

    coordinator = XiaomiHumidifier2Coordinator(
        hass,
        runtime_data.client,
        runtime_data.title,
    )
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = {
        "client": runtime_data.client,
        "coordinator": coordinator,
        "info": runtime_data.info,
        "model": runtime_data.model,
        "title": runtime_data.title,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
