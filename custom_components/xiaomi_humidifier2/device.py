"""Device helpers for Xiaomi Humidifier 2."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from miio import Device, DeviceException
from miio.deviceinfo import DeviceInfo
from miio.integrations.humidifier.zhimi.airhumidifier import AirHumidifier
from miio.integrations.humidifier.zhimi.airhumidifier_miot import AirHumidifierMiot

from homeassistant.const import CONF_HOST, CONF_MODEL, CONF_NAME, CONF_TOKEN

from .const import (
    CONF_MODEL_AUTO,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
    SUPPORTED_MODELS,
    is_deerma_model,
    is_miot_model,
)
from .deerma_jsq04 import DeermaHumidifierJsq04

_LOGGER = logging.getLogger(__name__)


class CannotConnectError(Exception):
    """Error to indicate we cannot connect to the device."""


class UnsupportedModelError(Exception):
    """Error to indicate an unsupported model."""


@dataclass(slots=True)
class XiaomiHumidifier2RuntimeData:
    """Runtime data for a config entry."""

    client: AirHumidifier | AirHumidifierMiot | DeermaHumidifierJsq04
    info: DeviceInfo
    model: str
    title: str


def instantiate_client(
    host: str, token: str, model: str
) -> AirHumidifier | AirHumidifierMiot | DeermaHumidifierJsq04:
    """Create a device client for the given model."""

    if is_deerma_model(model):
        return DeermaHumidifierJsq04(host, token, model=model, timeout=DEFAULT_TIMEOUT)

    if is_miot_model(model):
        return AirHumidifierMiot(host, token, model=model, timeout=DEFAULT_TIMEOUT)

    return AirHumidifier(host, token, model=model, timeout=DEFAULT_TIMEOUT)


def resolve_model(host: str, token: str, selected_model: str) -> str:
    """Return the resolved model string.

    For auto-detect, fetches device info from the network. If offline, falls back
    to the first supported deerma model so the entry can still load.
    """

    if selected_model != CONF_MODEL_AUTO:
        return selected_model

    try:
        info = Device(host, token, timeout=DEFAULT_TIMEOUT).info()
        if info.model in SUPPORTED_MODELS:
            return info.model
        _LOGGER.warning("Unsupported model %s, defaulting to jsq04 mapping", info.model)
        return info.model
    except DeviceException:
        _LOGGER.warning("Could not reach %s to detect model, will retry on next poll", host)
        return "deerma.humidifier.jsq04"


def validate_input(data: dict[str, Any]) -> XiaomiHumidifier2RuntimeData:
    """Validate the user input allows us to connect (used only during config flow)."""

    host = data[CONF_HOST]
    token = data[CONF_TOKEN]
    selected_model = data[CONF_MODEL]
    title = data.get(CONF_NAME) or DEFAULT_NAME

    try:
        info = Device(host, token, timeout=DEFAULT_TIMEOUT).info()
    except DeviceException as err:
        raise CannotConnectError from err

    detected_model = info.model
    if selected_model != CONF_MODEL_AUTO:
        resolved_model = selected_model
    elif detected_model in SUPPORTED_MODELS:
        resolved_model = detected_model
    else:
        raise UnsupportedModelError

    try:
        client = instantiate_client(host, token, resolved_model)
        client.status()
    except DeviceException as err:
        raise CannotConnectError from err

    return XiaomiHumidifier2RuntimeData(
        client=client,
        info=info,
        model=resolved_model,
        title=title,
    )
