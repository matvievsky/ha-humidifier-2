# Xiaomi Humidifier 2 for Home Assistant

Custom Home Assistant integration for Xiaomi/Smartmi humidifiers that expose a local `miIO` or `MIoT` interface.

## Supported models

| Model ID | Device |
| --- | --- |
| `zhimi.humidifier.v1` | Xiaomi Mi Air Humidifier |
| `zhimi.humidifier.ca1` | Smartmi Evaporative Humidifier |
| `zhimi.humidifier.cb1` | Smartmi Humidifier 2 |
| `zhimi.humidifier.cb2` | Smartmi Humidifier 2 Lite |
| `zhimi.humidifier.ca4` | Smartmi Evaporative Humidifier 2 |
| `deerma.humidifier.jsq04` | Mi Smart Humidifier 2 (MJJSQ04DY) |

## What it provides

- A native `humidifier` entity instead of a `fan` entity
- Local control over IP and token
- Power on/off
- Target humidity control
- Mode control
- Extra state attributes such as temperature, water level, child lock, buzzer, and dry mode when the device exposes them

## Installation

1. Copy `custom_components/xiaomi_humidifier2` into your Home Assistant config directory.
2. Restart Home Assistant.
3. Open `Settings -> Devices & services -> Add integration`.
4. Search for `Xiaomi Humidifier 2`.
5. Enter the device IP, token, and model.

## Notes

- `Auto detect` tries to read the real model from the device first.
- The device must be reachable from Home Assistant on the local network.
- If the model is not detected correctly, choose it manually.
- Legacy `miIO` models accept target humidity in steps of `10`; `zhimi.humidifier.ca4` accepts steps of `1`.
