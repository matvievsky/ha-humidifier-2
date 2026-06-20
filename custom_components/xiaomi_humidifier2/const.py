"""Constants for the Xiaomi Humidifier 2 integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "xiaomi_humidifier2"

CONF_MODEL_AUTO: Final = "auto"

DEFAULT_NAME: Final = "Xiaomi Humidifier 2"
DEFAULT_SCAN_INTERVAL: Final = 30
DEFAULT_TIMEOUT: Final = 5

LEGACY_MODELS: Final[tuple[str, ...]] = (
    "zhimi.humidifier.v1",
    "zhimi.humidifier.ca1",
    "zhimi.humidifier.cb1",
    "zhimi.humidifier.cb2",
)

MIOT_MODELS: Final[tuple[str, ...]] = ("zhimi.humidifier.ca4",)

DEERMA_MODELS: Final[tuple[str, ...]] = (
    "deerma.humidifier.jsq04",
    "deerma.humidifier.jsq2g",
)

SUPPORTED_MODELS: Final[tuple[str, ...]] = (*LEGACY_MODELS, *MIOT_MODELS, *DEERMA_MODELS)

MODE_LABELS: Final[dict[str, str]] = {
    CONF_MODEL_AUTO: "Auto detect",
    "zhimi.humidifier.v1": "Xiaomi Mi Air Humidifier (zhimi.humidifier.v1)",
    "zhimi.humidifier.ca1": "Smartmi Evaporative Humidifier (zhimi.humidifier.ca1)",
    "zhimi.humidifier.cb1": "Smartmi Humidifier 2 (zhimi.humidifier.cb1)",
    "zhimi.humidifier.cb2": "Smartmi Humidifier 2 Lite (zhimi.humidifier.cb2)",
    "zhimi.humidifier.ca4": "Smartmi Evaporative Humidifier 2 (zhimi.humidifier.ca4)",
    "deerma.humidifier.jsq04": "Mi Smart Humidifier 2 (deerma.humidifier.jsq04)",
    "deerma.humidifier.jsq2g": "Mi Smart Humidifier 2 (deerma.humidifier.jsq2g)",
}


def is_miot_model(model: str) -> bool:
    """Return whether the device model uses the zhimi MIoT implementation."""

    return model in MIOT_MODELS


def is_deerma_model(model: str) -> bool:
    """Return whether the device model is a Deerma humidifier."""

    return model in DEERMA_MODELS
