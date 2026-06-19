"""Deerma Mi Smart Humidifier 2 (deerma.humidifier.jsq04) MiOT device."""

from __future__ import annotations

import enum
from typing import Any, Optional

from miio.miot_device import DeviceStatus, MiotDevice

_MIOT_MAPPING: dict[str, dict] = {
    # Humidifier (siid=2)
    "power": {"siid": 2, "piid": 1},
    "fault": {"siid": 2, "piid": 2},
    "mode": {"siid": 2, "piid": 5},       # 1=Low, 2=Mid, 3=Humidity
    "target_humidity": {"siid": 2, "piid": 6},  # [40, 80] step 1
    # Environment (siid=3)
    "relative_humidity": {"siid": 3, "piid": 1},
    "temperature": {"siid": 3, "piid": 7},
    # Alarm (siid=5)
    "buzzer": {"siid": 5, "piid": 1},
    # Light (siid=6)
    "led_light": {"siid": 6, "piid": 1},
    # Other (siid=7)
    "water_shortage_fault": {"siid": 7, "piid": 1},
    "tank_filed": {"siid": 7, "piid": 2},
}

MODEL_JSQ04 = "deerma.humidifier.jsq04"


class OperationMode(enum.Enum):
    Low = 1
    Mid = 2
    Humidity = 3


class DeermaJsq04Status(DeviceStatus):
    """Status for deerma.humidifier.jsq04."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    @property
    def is_on(self) -> bool:
        return bool(self.data.get("power"))

    @property
    def power(self) -> str:
        return "on" if self.is_on else "off"

    @property
    def mode(self) -> OperationMode:
        try:
            return OperationMode(self.data["mode"])
        except (ValueError, KeyError):
            return OperationMode.Low

    @property
    def target_humidity(self) -> Optional[int]:
        return self.data.get("target_humidity")

    @property
    def humidity(self) -> Optional[int]:
        return self.data.get("relative_humidity")

    @property
    def temperature(self) -> Optional[float]:
        v = self.data.get("temperature")
        return float(v) if v is not None else None

    @property
    def buzzer(self) -> Optional[bool]:
        return self.data.get("buzzer")

    @property
    def led_light(self) -> Optional[bool]:
        return self.data.get("led_light")

    @property
    def water_shortage_fault(self) -> Optional[bool]:
        return self.data.get("water_shortage_fault")

    @property
    def tank_filed(self) -> Optional[bool]:
        return self.data.get("tank_filed")


class DeermaHumidifierJsq04(MiotDevice):
    """Deerma Mi Smart Humidifier 2."""

    _mappings = {MODEL_JSQ04: _MIOT_MAPPING}

    def status(self) -> DeermaJsq04Status:
        return DeermaJsq04Status(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    def on(self) -> None:
        return self.set_property("power", True)

    def off(self) -> None:
        return self.set_property("power", False)

    def set_target_humidity(self, humidity: int) -> None:
        if not 40 <= humidity <= 80:
            raise ValueError(f"Target humidity must be 40–80, got {humidity}")
        return self.set_property("target_humidity", humidity)

    def set_mode(self, mode: OperationMode) -> None:
        return self.set_property("mode", mode.value)
