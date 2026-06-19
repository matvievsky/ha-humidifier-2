"""Coordinator for Xiaomi Humidifier 2."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from miio import DeviceException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class XiaomiHumidifier2Coordinator(DataUpdateCoordinator[Any]):
    """Poll the device state."""

    def __init__(self, hass: HomeAssistant, client: Any, title: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=title,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> Any:
        """Fetch the latest device status."""

        try:
            return await self.hass.async_add_executor_job(self.client.status)
        except DeviceException as err:
            raise UpdateFailed(f"Unable to update Xiaomi humidifier state: {err}") from err
