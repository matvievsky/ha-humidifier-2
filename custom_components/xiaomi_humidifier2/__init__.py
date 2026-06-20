"""The Xiaomi Humidifier 2 integration."""

from __future__ import annotations

import logging

from miio import DeviceException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant

from .coordinator import XiaomiHumidifier2Coordinator
from .const import CONF_MODEL_AUTO, DEFAULT_NAME, DEFAULT_TIMEOUT, SUPPORTED_MODELS
from .device import instantiate_client, resolve_model

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.HUMIDIFIER, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xiaomi Humidifier 2 from a config entry."""

    host = entry.data[CONF_HOST]
    token = entry.data[CONF_TOKEN]
    model = entry.data.get("model", CONF_MODEL_AUTO)
    title = entry.data.get(CONF_NAME) or entry.title or DEFAULT_NAME

    resolved_model = await hass.async_add_executor_job(resolve_model, host, token, model)

    client = instantiate_client(host, token, resolved_model)

    coordinator = XiaomiHumidifier2Coordinator(hass, client, title)

    # Soft first refresh — entities become unavailable if offline, but HA keeps running.
    await coordinator.async_refresh()

    entry.runtime_data = {
        "client": client,
        "coordinator": coordinator,
        "info": coordinator.device_info_cache,
        "model": resolved_model,
        "title": title,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
